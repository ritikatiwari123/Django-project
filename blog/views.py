from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.views.decorators.http import require_POST

from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


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
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, 'detail.html', {'post': post,
                                                                'comments': comments,
                                           'form': form})


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


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a comment object without saving it to the database
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'comment.html', {'post':post,
                                                                'form': form,
                                                                 'comment': comment})