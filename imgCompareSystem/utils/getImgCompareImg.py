import os
import shutil

from sklearn.utils import shuffle

save_path = '/disk1/chenzewen/EngineeringProject/OPPO/imgCompare/imgCompareSystem/source/ImgTest'
save_name = 'Teacher_IQA_Full_MDESSIM_DRL_Test'

save_path = os.path.join(save_path, save_name)

print(save_path)
if not os.path.isdir(save_path):
    os.makedirs(save_path)


ref_img_path = '/disk1/chenzewen/EngineeringProject/OPPO/OPPOProject/DRL/TinyISP_DRL/TinyISP_DRL/DATAS/tinyISP_61'
pred_img_path = '/disk1/chenzewen/EngineeringProject/OPPO/OPPOProject/DRL/TinyISP_DRL/TinyISP_DRL/results_test/teacherIQA_Full_MDESSIM_6400/final_images'

for case in os.listdir(ref_img_path):
    try:
        index = int(case.replace('Case', ''))
        assert os.path.isfile(os.path.join(pred_img_path, '{}.png'.format(index)))

        save_case_path = os.path.join(save_path, 'Case{}'.format(str(index).zfill(2)))
        if not os.path.isdir(save_case_path):
            os.makedirs(save_case_path)

        for file in os.listdir(os.path.join(ref_img_path, case)):
            if 'Gt' in file:
                shutil.copy(os.path.join(ref_img_path, case, file), os.path.join(save_case_path, '{}_GT.png'.format(case)))
                break
        
        assert os.path.isfile(os.path.join(save_case_path, '{}_GT.png'.format(case)))

        shutil.copy(os.path.join(pred_img_path, '{}.png'.format(index)), os.path.join(save_case_path, '{}_Pred.png'.format(case)))
    except:
        print(case)
        continue