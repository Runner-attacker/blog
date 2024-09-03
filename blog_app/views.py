from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from blog_app.forms import PostForm
from blog_app.models import Post
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin


class PostListView(ListView):
    model = Post
    template_name = "post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        posts = Post.objects.filter(published_at__isnull=False).order_by(
            "-published_at"
        )
        return posts


# Create your views here.


class PostDetailView(DetailView):
    model = Post
    template_name = "post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(
            pk=self.kwargs["pk"],
            published_at__isnull=False,
        )
        return queryset


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "draft_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        queryset = Post.objects.filter(published_at__isnull=True).order_by(
            "-published_at"
        )
        return queryset


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "draft_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(
            pk=self.kwargs["pk"],
            published_at__isnull=True,
        )
        return queryset


@login_required
def draft_detail(request, pk):
    post = Post.objects.get(pk=pk, published_at__isnull=True)
    return render(
        request,
        "draft_detail.html",
        {"post": post},
    )


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect("post-list")


@login_required
def post_delete(request, pk):
    post = Post.objects.get(pk=pk)
    post.delete()
    return redirect("post-list")


class PostPublishView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        return redirect("post-list")


class PostCreateView(LoginRequiredMixin, CreateView):
    model = (Post,)
    template_name = "post_create.html"
    form_class = PostForm
    # success_url = reverse_lazy("post-list")

    def get_success_url(self) -> str:
        return reverse_lazy("draft-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "post_create.html"
    form_class = PostForm

    def get_success_url(self):
        post = self.get_object()
        if post.published_at:
            return reverse_lazy("post-detail", kwargs={"pk": post.pk})
        else:
            return reverse_lazy("draft-detail", kwargs={"pk": post.pk})

    """
from django.shortcuts import render, redirect
from .forms import PostForm

def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # Create a Post instance but don't save to the database yet
            post.author = request.user  # Set the author field to the current user
            post.coauthor = request.user.get_full_name()  # Set the coauthor field to the user's full name
            post.save()  # Save the Post instance to the database
            return redirect('post_detail', pk=post.pk)  # Redirect to the post detail page
    else:
        form = PostForm()  # Create an empty form instance for GET requests

    return render(request, 'post_create.html', {'form': form})

    
    
    """
