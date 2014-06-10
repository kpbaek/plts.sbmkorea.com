from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from plts.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.urlresolvers import reverse
from plts.digitChecker import *
import json

# you should put @csrf_exempt when data is posted from android
@transaction.commit_manually
@csrf_exempt
def upload_manufacturing_history(request):
	try:
		print request.POST
		data = request.POST.get('data')
		print data.encode('utf-8')
		data = json.loads(data)
		
		manufacturing_type_name = data['manufacturing_type_name']
		product_barcode = data['product_barcode']
		part_barcode = data['part_barcode']
		worker_barcode = data['worker_barcode']
		repair_error_type_id_str = data['repair_error_type']
		remark = data['remark']
		
		#get product
		product_model_id = int(product_barcode[1:3])
		product_model = ProductModel.objects.get(id=product_model_id)
		product_status = ProductStatus.objects.get(id=1)
		product, product_created = Product.objects.get_or_create(barcode=product_barcode, product_model=product_model, defaults={'product_status':product_status})
	
		#get worker
		worker = Worker.objects.get(barcode=worker_barcode)
		
		#get part
		part_class_id = int(part_barcode[1:3])
		part_version = int(part_barcode[3:5])
		company_id = int(part_barcode[5:7])
		part_class = PartClass.objects.get(id=part_class_id)
		part_type = PartType.objects.get(part_class=part_class_id, version=part_version, company=company_id)
		part, part_created = Part.objects.get_or_create(barcode=part_barcode, part_type=part_type)

		#create manufacturing history
		manufacturing_type = ManufacturingType.objects.get(name=manufacturing_type_name)
		
		if(repair_error_type_id_str != ""):
			repair_error_type_id = int(repair_error_type_id_str)
			repair_error_type = RepairErrorType.objects.get(id=repair_error_type_id)
		else:
			repair_error_type = None
	
		manufacturingHistory = ManufacturingHistory.objects.create(
			manufacturing_type=manufacturing_type,
			product=product,
			part=part,
			repair_error_type=repair_error_type,
			remark=remark,
			worker=worker
		)

		transaction.commit()
		return HttpResponse("success")
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		transaction.rollback()
		return HttpResponse(e.message)


@transaction.commit_manually
@csrf_exempt
def bulk_production(request):
	try:
		print "bulk production"
		print request.POST
		data = request.POST.get('data')
		print data.encode('utf-8')
		data = json.loads(data)
		
		manufacturing_type_name = data['manufacturing_type_name']
		product_barcode = data['product_barcode']
		part_barcode_list = data['part_barcode']
		worker_barcode = data['worker_barcode']
		repair_error_type_id_str = ""
		remark = ""
		
		#get product
		product_model_id = int(product_barcode[1:3])
		product_model = ProductModel.objects.get(id=product_model_id)
		product_status = ProductStatus.objects.get(id=1)
		product, product_created = Product.objects.get_or_create(barcode=product_barcode, product_model=product_model, defaults={'product_status':product_status})
		
		#get worker
		worker = Worker.objects.get(barcode=worker_barcode)
		manufacturing_type = ManufacturingType.objects.get(name=manufacturing_type_name)
		if(repair_error_type_id_str != ""):
			repair_error_type_id = int(repair_error_type_id_str)
			repair_error_type = RepairErrorType.objects.get(id=repair_error_type_id)
		else:
			repair_error_type = None
		
	
		for part_barcode in part_barcode_list:
			#get part
			part_class_id = int(part_barcode[1:3])
			part_version = int(part_barcode[3:5])
			company_id = int(part_barcode[5:7])
			part_class = PartClass.objects.get(id=part_class_id)
			part_type = PartType.objects.get(part_class=part_class_id, version=part_version, company=company_id)
			part, part_created = Part.objects.get_or_create(barcode=part_barcode, part_type=part_type)
	
			#create manufacturing history
			
			manufacturingHistory = ManufacturingHistory.objects.create(
				manufacturing_type=manufacturing_type,
				product=product,
				part=part,
				repair_error_type=repair_error_type,
				remark=remark,
				worker=worker
			)

		transaction.commit()
		return HttpResponse("success")
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		transaction.rollback()
		return HttpResponse(e.message)

