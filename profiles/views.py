from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse

from shop.models import Product
from .forms import ProfileForm, CustomChangePasswordForm
from .models import Profile


def _get_or_create_profile(user):
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'email_verify': user.email,
            'slug': f'profile-{user.id}',
        }
    )
    if created or not profile.slug:
        profile.save()
    return profile


@login_required
def profiles(request):
    profile = _get_or_create_profile(request.user)
    product_list = Product.objects.order_by('-name')
    return render(request, 'profiles/index.html', {'profile': profile, 'product_list': product_list})


@login_required
def profile(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    return render(request, 'profiles/profile.html', {'profile': profile})


@login_required
def edit_profile(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    if profile.user_id != request.user.id:
        messages.error(request, "You can only edit your own profile.")
        return redirect(profile.get_absolute_url())

    form = ProfileForm(instance=profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            updated_profile = form.save()
            request.user.first_name = updated_profile.first_name
            request.user.last_name = updated_profile.last_name
            request.user.email = updated_profile.email or ''
            request.user.save()
            messages.success(request, "{} {}'s profile updated."
                             .format(form.cleaned_data["first_name"],
                                     form.cleaned_data["last_name"]))
            return HttpResponseRedirect(profile.get_absolute_url())
    return render(request, "profiles/edit-profile.html", {'form': form, 'profile': profile})


@login_required
def change_password(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug)
    if profile.user_id != request.user.id:
        messages.error(request, "You can only change your own password.")
        return redirect(profile.get_absolute_url())

    if request.method == 'POST':
        form = CustomChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(profile.get_absolute_url())
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomChangePasswordForm(request.user)
    return render(request, 'profiles/change-password.html', {
        'form': form,
        'profile': profile,
    })
