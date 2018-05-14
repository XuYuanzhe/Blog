from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
import markdown
from django.utils.html import strip_tags


class Category(models.Model):
	"""
    Django 要求模型必须继承 models.Model 类
    CharField 指定了分类名 name 的数据类型，CharField 是字符型
    CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库。
    """
	name = models.CharField(max_length = 100)
	def __str__(self):
		return self.name

class Tag(models.Model):
	name = models.CharField(max_length = 100)
	def __str__(self):
		return self.name
	
@python_2_unicode_compatible		
class Post(models.Model):
	# 文章标题
	title = models.CharField(max_length = 70)
	# 文章正文
	# TextField，可存储大段文本
	body = models.TextField()
	# 文章的创建时间
	# DateTimeField 存储时间的字段用 
	created_time = models.DateTimeField()
	# 文章的最后一次修改时间
	modified_time = models.DateTimeField()
	# 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
	excerpt = models.CharField(max_length = 200,blank = True)
	# 文章分类
	# 一篇文章一个分类，一个分类对应多个文章，一对多
	category = models.ForeignKey(Category)
	# 文章标签
	# 一篇文章多个标签，一个标签给多个文章使用，多对多
	tags = models.ManyToManyField(Tag,blank = True)
	# 文章作者
	# 一对多 User 是Django给的写好的
	author = models.ForeignKey(User)
	# 新增阅读量字段
	views = models.PositiveIntegerField(default=0)


	def __str__(self):
		return self.title
	def get_absolute_url(self):
		return reverse('blog:detail',kwargs={'pk':self.pk})
	# 阅读量自增方法
	def increase_views(self):
		self.views += 1
		self.save(update_fields=['views'])
	# 复写方法摘要
	def save(self, *args, **kwargs):
		# 如果没有填写摘要
		if not self.excerpt:
			# 首先实例化一个 Markdown 类，用于渲染 body 的文本
			md = markdown.Markdown(extensions=[
				'markdown.extensions.extra',
				'markdown.extensions.codehilite',
			])
			# 先将 Markdown 文本渲染成 HTML 文本
			# strip_tags 去掉 HTML 文本的全部 HTML 标签
			# 从文本摘取前 54 个字符赋给 excerpt
			self.excerpt = strip_tags(md.convert(self.body)).split()[0] + '...'

		# 调用父类的 save 方法将数据保存到数据库中
		super(Post, self).save(*args, **kwargs)

	class Meta:
		ordering = ['-created_time']