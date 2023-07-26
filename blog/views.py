from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage

from .forms import EmailPostForm
from .models import Post


def post_list(request):
    posts = Post.published.all()
    # pagination with 3 posts per page
    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    try:
        post_list = paginator.page(page_number)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'list.html', {'posts': post_list})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request, 'detail.html', {'post': post})


def post_share(request, post_id):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, id=post_id)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n"\
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'ritiika.dadhich@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'share.html', {'post':post,
                                          'form': form,
                                          'sent': sent})
