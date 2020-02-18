from django.shortcuts import render,HttpResponse
from crm import models
from PerfectCRMv1 import settings
import os,json,time
# Create your views here.

def stu_my_classes(request):
    return render(request, "student/my_classes.html")

def studyrecords(request,enroll_obj_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_obj_id)
    return render(request,"student/studyrecords.html",{"enroll_obj":enroll_obj})

def homework_detail(request,studyrecord_id):
    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)

    if request.method == "POST":
        print(request.FILES)
        # class_id/course_record_id/studyrecord_id
        homework_path = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/".format(base_dir=settings.HOMEWORK_DATA,
                                                                                            class_id=studyrecord_obj.student.enrolled_class_id,
                                                                                            course_record_id=studyrecord_obj.course_record_id,
                                                                                            studyrecord_id=studyrecord_obj.id
                                                                                            )
        if not os.path.isdir(homework_path):
            os.makedirs(homework_path,exist_ok=True)



        for k,file_obj in request.FILES.items():
            with open("%s/%s" %(homework_path,file_obj.name),'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

        file_lists = []
        for file_name in os.listdir(homework_path):
            f_path = "%s/%s" %(homework_path,file_name)
            modify_time = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(os.stat(f_path).st_ctime))
            file_lists.append([file_name,os.stat(f_path).st_size,modify_time])
        print("file_lists",file_lists)

        if request.method == "POST":

            return HttpResponse(json.dumps({"status":0,
                                            'msg':"file upload success",
                                            "file_lists":file_lists}))
    return render(request,"student/homework_detail.html",{"studyrecord_obj":studyrecord_obj})