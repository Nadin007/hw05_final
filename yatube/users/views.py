from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages
from django.shortcuts import redirect, render
from posts.models import User

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("index")
    template_name = "signup.html"

    def create_new_user(self, form):
        User.objects.create(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            avatar=form.cleaned_data['avatar'],
            bio=form.cleaned_data['bio'])

    def dispatch(self, request, *args, **kwargs):
        form = CreationForm()
        if request.method == 'POST':
            form = CreationForm(
                request.POST or None, files=request.FILES or None)
            if form.is_valid():
                # self.create_new_user(form)
                form.save(commit=True)
                messages.success(
                    request, u"Registration successfully completed!")
                return redirect("/")
        context = {
            'form': form
        }
        return render(request, self.template_name, context)
