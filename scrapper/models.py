from django.db import models

# Create your models here.

class productPagesScrapper(models.Model):
	source = models.CharField(max_length=200, null=True, blank=True)
	category = models.CharField(max_length=200, null=True, blank=True)
	productID = models.CharField(max_length=50, null=True, blank=True)
	title_en = models.CharField(max_length=500, null=True, blank=True)
	title_ar = models.CharField(max_length=500, null=True, blank=True)
	description_en = models.BooleanField(default=False)
	description_ar = models.BooleanField(default=False)
	last_checked = models.DateTimeField(auto_now_add=True, blank=True)
	price = models.CharField(max_length=20, null=True, blank=True)
	old_price = models.CharField(max_length=20, null=True, blank=True)
	batchname = models.CharField(max_length=500, null=True, blank=True)

	def __str__(self):
		return self.productID

	@property
	def get_parent_asin(self):
		parents = self.totalvariations_set.all()
		if parents:
			return parents[0].parent_asin
		else:
			return None

	class Meta:
		verbose_name_plural="Product Pages Scrapper"

class productDetails(models.Model):
	productID = models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	attributes = models.CharField(max_length=512, null=True, blank=True)
	values = models.CharField(max_length=1024, null=True, blank=True)
	language = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return self.productID.productID

	class Meta:
		verbose_name_plural="Product Details"

class productImages(models.Model):
	productID = models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	image = models.CharField(max_length=512, null=True, blank=True)

	def __str__(self):
		return self.productID.productID

	class Meta:
		verbose_name_plural="Product Images"

class productHighlights(models.Model):
	productID = models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	highlight = models.TextField(null=True, blank=True)
	language = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return self.productID.productID

	class Meta:
		verbose_name_plural="Product Highlights"

class productDescription(models.Model):
	productID= models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	long_description = models.TextField(null=True, blank=True)
	language = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return self.productID.productID

	class Meta:
		verbose_name_plural="Product Description"

class variationSettings(models.Model):
	productID = models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	parent_asin = models.CharField(max_length=50, null=True, blank=True)
	current_asin = models.CharField(max_length=50, null=True, blank=True)
	dimension = models.CharField(max_length=50, null=True, blank=True)
	dimension_val_en = models.TextField(null=True, blank=True)
	dimension_val_ar = models.TextField(null=True, blank=True)
	title_en = models.CharField(max_length=500, null=True, blank=True)
	title_ar = models.CharField(max_length=500, null=True, blank=True)
	images = models.TextField(null=True,blank=True)
	description_en = models.BooleanField(default=False)
	description_ar = models.BooleanField(default=False)
	price = models.CharField(max_length=20, null=True, blank=True)
	old_price = models.CharField(max_length=20, null=True, blank=True)
	available = models.BooleanField(default=False)
	last_checked = models.DateTimeField(auto_now_add=True, blank=True)

	def __str__(self):
		return self.current_asin

	class Meta:
		verbose_name_plural="Variation Settings"

class totalVariations(models.Model):
	productID = models.ForeignKey(productPagesScrapper, null=True, on_delete=models.CASCADE)
	parent_asin = models.CharField(max_length=50, null=True, blank=True)
	name_en = models.CharField(max_length=50, null=True, blank=True)
	name_ar = models.CharField(max_length=50, null=True, blank=True)
	value_en = models.TextField(null=True, blank=True)
	value_ar = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.productID.productID

	class Meta:
		verbose_name_plural="Total Variations"

class fc_grades(models.Model):
	grade = models.CharField(max_length=60, null=True, blank=True)
	cond = models.CharField(max_length=300, null=True, blank=True)
	description = models.CharField(max_length=1500, null=True, blank=True)
	color = models.CharField(max_length=30, null=True, blank=True)
	grade_ar = models.TextField(null=True, blank=True)
	cond_ar = models.TextField(null=True, blank=True)
	description_ar = models.TextField(null=True, blank=True)
	grade_code = models.CharField(max_length=384, null=True, blank=True)
	google_grade = models.CharField(max_length=765, null=True, blank=True)

	def __str__(self):
		return self.grade_code

	class Meta:
		verbose_name_plural="FC_Grades"