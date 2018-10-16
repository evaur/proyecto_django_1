from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django import forms
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User

#Para el xlsx
from django.http import HttpResponse, HttpResponseBadRequest
import io
import xlsxwriter
from datetime import datetime
import openpyxl


# Create your views here.
def post_list(request):
    posts = Post.objects.filter(active=True).order_by('published_date').reverse()
    # posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    # renderizará (construirá) nuestra plantilla blog/post_list.html
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('/', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.active = False
    post.save()
    return redirect('/')

def export_posts_xls(request):
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Sheet header, first row
    row_num = 0
    columns = ['Id', 'Author', 'Title', 'Text', 'Fecha de publicación', ]
    
    #font_style = xlwt.XFStyle()
    #font_style.font.bold = True  

    for col_num in range(len(columns)):
        worksheet.write(row_num, col_num, columns[col_num])#, font_style

    rows = Post.objects.all().values_list('id', 'author', 'title', 'text', 'published_date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            if isinstance((row[col_num]), datetime) :
                #vigilar con las fechas
                worksheet.write(row_num, col_num, str(row[col_num]))#, font_style)
            else :
                worksheet.write(row_num, col_num, row[col_num])#, font_style)
    
    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + '.xlsx'

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response

def import_posts_xls(request):
    if request.method == "POST":
        #form = PostForm(request.POST)
        #print(form.is_valid())
        excel_file = request.FILES['excel_file']
        wb = openpyxl.load_workbook(excel_file)
        ws = wb['Hoja1']
        #llegir dades 
        llista_models = []
        for row in ws.rows:
            
            author=row[0].value
            title=row[1].value
            text=row[2].value
            active=bool(row[3].value)
            published_date=datetime.now()

            #mirar si existe el usuario author
            exist_user = User.objects.filter(username=author)
           
            if exist_user.exists():
                user = User.objects.get(username=author)
                objecte_post = Post(
                    author=user, 
                    title=title,
                    text=text,
                    active=active,
                    published_date=published_date
                )
                llista_models.append(objecte_post)
        Post.objects.bulk_create(llista_models)
    return redirect('/')
