from django.shortcuts import render
from cl_app.models import Listing, Profile, ListingType, City
from django.views.generic.base import TemplateView
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse_lazy


class IndexView(ListView):
    template_name = "index.html"
    model = ListingType

    def get_queryset(self):
        return ListingType.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.all()

        if self.request.user.is_authenticated():
            context["profile"] = Profile.objects.get(user=self.request.user)
        else:
            context["login_form"] = AuthenticationForm()
        return context

class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    model = User

class ListingCreateView(CreateView):
    model = Listing
    fields = ['listing_city', 'title', 'price', 'description', 'photo']
    # success_url = reverse_lazy("profile_detail_view")  # change to listing page

    def form_valid(self, form):
        listing = form.save(commit=False)
        listing.user = self.request.user
        category_id = self.kwargs.get('categorypk')
        listing.category = ListingType.objects.get(id=category_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("listing_detail_view", args = (self.object.id,))

class ListingUpdateView(UpdateView):
    model = Listing
    fields = ['listing_city', 'title', 'price', 'description', 'photo']

    def get_success_url(self):
        return reverse_lazy("listing_detail_view", args = (self.object.id,))

class ListingDeleteView(DeleteView):
    model = Listing
    success_url = reverse_lazy('profile_view')

    def get_object(self, queryset=None):
        listing = super().get_object()
        if not listing.user == self.request.user:
            raise Http404
        return listing

class ListingTypeCreateView(CreateView):
    # model = ListingType
    fields = ['parent']
    template_name = 'cl_app/listingtype_form.html'

    def get_queryset(self):
        return ListingType.subcat.filter(parent=None)


class CityListView(ListView):
    template_name = 'cl_app/city_listing_list.html'
    model = ListingType

    def get_queryset(self):
        return ListingType.objects.filter(parent=None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city_id = self.kwargs.get('city')
        context['city'] = City.objects.get(id=city_id)
        context['cities'] = City.objects.all()

        if self.request.user.is_authenticated():
            context["profile"] = Profile.objects.get(user=self.request.user)
        else:
            context["login_form"] = AuthenticationForm()
        return context


class CityCategoryListView(ListView):
    model = Listing

    def get_queryset(self, **kwargs):
        city_id = self.kwargs.get('citypk')
        category_id = self.kwargs.get('categorypk')
        return Listing.objects.filter(listing_city=city_id).filter(category=category_id)

    def get_context_data(self, **kwargs):
        city_id = self.kwargs.get('citypk')
        category_id = self.kwargs.get('categorypk')
        context = super().get_context_data(**kwargs)
        context['city'] = City.objects.get(id=city_id)
        context['category'] = ListingType.objects.get(id=category_id)
        return context


class ListingDetailView(DetailView):
    model = Listing

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context['profile'] = Profile.objects.get(user=self.request.user)
        return context


class CategoryListView(ListView):
    model = Listing

    def get_queryset(self, **kwargs):
        category_id = self.kwargs.get('categorypk', None)
        return Listing.objects.filter(category=category_id)


class ProfileView(UpdateView):
    fields = ['profile_city', 'preferred_contact']
    success_url = reverse_lazy("index_view")
    # model = Profile
    # Why dont I have to declare a model here??
    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_listings'] = Listing.objects.filter(user=self.request.user)
        return context