import cv2
import os
from collections import deque
import csv
import sys

class Video_labeling:


    queue_size = 500
    video_show = 0
    video_que = deque()
    
    
    video_list = []
    video_frame = 0
    video_cnt = 0
    video_max = 0
    video_path = ''
    violation = [0,1,2,3,4,5]
    cap = ''
    state = 'end'
    csv_datafile = ''




    def __init__(self, video_path):
        self.video_path = video_path
        file_list = os.listdir(video_path)
        video_list = []

        # 파일이름중 동영상 파일 이름만 가져오기. 기본값은 AVI,mp4 가져옴.
        for file_name in file_list:
            extension = file_name.split('.')[-1]
            if extension == 'AVI' or extension == 'mp4':
                video_list.append(file_name)

        # 영상 순서대로 틀기 위해 정렬 한번 해줌
        video_list.sort()
        self.video_list = video_list
        self.video_max = len(video_list)-1
        self.have_savefile()
        print('초기 영상을 불러옵니다. 잠시만 기다려 주세요')
        self.queue_update(isFirst = True)
        
        
        
        
        
    def have_savefile(self):
        csv_name = os.path.join(self.video_path,'save_file.csv')
        
        if os.path.exists(csv_name):
            print('저장파일이 존재합니다. 마지막 지점부터 시작합니다.')
            self.csv_datafile = open(csv_name, 'r')
            reader = list(csv.reader(self.csv_datafile))
            self.video_cnt = self.video_list.index(reader[-1][2]) -1
            self.violation[0] = int(reader[-1][0])
            self.csv_datafile.close()
            
            csv_file = open(csv_name, 'a', newline='')
            wr = csv.writer(csv_file)
            self.csv_datafile = wr
        else:
            print('저장파일이 없습니다. 처음부터 시작합니다.')
            csv_file = open(csv_name, 'w', newline='')
            header = ['index','start_file', 'end_file', 'start_frame', 'end_frame','case']
            
            wr = csv.writer(csv_file)
            wr.writerow(header)
            self.csv_datafile = wr
            





        
    def queue_update(self,isFirst = False):
    
        if isFirst:
            self.cap = cv2.VideoCapture(os.path.join(self.video_path,self.video_list[self.video_cnt]))
            self.video_frame = 0
            
            while(len(self.video_que) != queue_size):
                state, frame = self.cap.read()
                
                if state == False:
                    self.video_cnt += 1
                    self.cap = cv2.VideoCapture(os.path.join(self.video_path,self.video_list[self.video_cnt]))
                    self.video_frame = 0
                    
                state, frame = self.cap.read()
                self.video_frame += 1
                self.video_que.append([self.video_list[self.video_cnt],frame,self.video_frame])
            
#        if self.video_show < self.queue_size//2 :
#            return
        
        while(self.video_show > self.queue_size//2 ):

            state,frame = self.cap.read()
            
            if state == False:
                if self.video_cnt == self.video_max:
                    print('모든 영상을 확인하였습니다. 종료합니다.')
                    self.finish()
                else:
                    self.video_cnt += 1
                    self.cap = cv2.VideoCapture(os.path.join(self.video_path,self.video_list[self.video_cnt]))
                    self.video_frame = 0
                    continue
            self.video_que.popleft()
            self.video_frame += 1
            self.video_que.append([self.video_list[self.video_cnt],frame,self.video_frame])
            self.video_show -= 1
                
        

    
    def visualrize(self):
#        if self.video_cnt == self.video_max:
#            cv2.destroyAllWindows()
#            return False
        #print(self.video_show,self.video_que[self.video_show][2])
        ㅔㄱ
        cv2.imshow('Data Labeling',self.video_que[self.video_show][1])
        key_return = cv2.waitKey(0)
        
        #TODO 뒤로가기 왼쪽 방향키
        if key_return == 2:
            self.before_frame()
            
        #TODO 앞으로가기 오른쪽 방향키
        elif key_return == 3:
            self.after_frame()
        #TODO 라벨링 엔터
        elif key_return == 13:
            self.labeling()
        # 종료 ESC
        elif key_return == 27:
            self.finish()
            
        else:
            #print(key_return)
            self.video_show += 1
        self.queue_update()
            
        return True
            
        
            
    
    def before_frame(self):
        self.video_show -= 5
        self.video_frame -= 5
        
    def after_frame(self):
        self.video_show += 5
        self.video_frame += 5
        
    def labeling(self):
    
        if self.state == 'end':
            while True:
                print('위반 시작지점입니다')
                print('맞다면 Enter')
                print('틀리다면 Back Space를 눌러주세요')

                key_return = cv2.waitKey(0)
                #엔터
                if key_return == 13:
                    self.violation[0] += 1
                    self.violation[1] = self.video_list[self.video_cnt]
                    self.violation[3] = self.video_que[self.video_show][2]
                    self.state = 'start'
                    return
                #Back Space
                elif key_return == 127:
                    return
                else:
                    print('잘못된 입력입니다 다시 입력해주세요')
                    
        if self.state == 'start':
            print('위반 종료지점입니다')
            print('맞다면 Enter')
            print('틀리다면 Back Space를 눌러주세요')
            while True:
                key_return = cv2.waitKey(0)
                
                #엔터
                if key_return == 13:
                    self.violation[2] = self.video_list[self.video_cnt]
                    self.violation[4] = self.video_que[self.video_show][2]
                    break
                #Back Space
                elif key_return == 127:
                    return
                else:
                    print('잘못된 입력입니다 다시 입력해주세요')
                    
            
                    
            print('위반 사항을 골라주세요')
            print('1 정지선 위반')
            print('2 신호 위반')
            print('3 중앙선 침범')
            print('4 진로변경 위반')
            print('5 제차 조작 신호 불이행')
            print('확인 Enter, 취소 Back Space')
            
            while True:
            
                key_return = cv2.waitKey(0)
                
                #1
                if key_return == 49:
                    while True :
                        print('1. 정지선위반이 맞습니까?')
                        key_return = cv2.waitKey(0)
                        if key_return == 13:
                            self.violation[5] = 1
                            self.csv_datafile.writerow(self.violation)
                            print('등록이 완료되었습니다')
                            self.state ='end'
                            return
                        elif key_return == 127:
                            print('다시 입력해주세요')
                            break
                        print('잘못된 입력입니다 다시 입력해주세요')
                    
                    
                #2
                elif key_return == 50:
                    while True :
                        print('2. 신호위반이 맞습니까?')
                        key_return = cv2.waitKey(0)
                        if key_return == 13:
                            self.violation[5] = 2
                            self.csv_datafile.writerow(self.violation)
                            print('등록이 완료되었습니다')
                            self.state = 'end'
                            return
                        elif key_return == 127:
                            print('다시 입력해주세요')
                            break
                        print('잘못된 입력입니다 다시 입력해주세요')
                
                #3
                elif key_return == 51:
                    while True :
                        print('3. 중앙선 침범위반이 맞습니까?')
                        key_return = cv2.waitKey(0)
                        if key_return == 13:
                            self.violation[5] = 3
                            self.csv_datafile.writerow(self.violation)
                            print('등록이 완료되었습니다')
                            self.state = 'end'
                            return
                        elif key_return == 127:
                            print('다시 입력해주세요')
                            break
                        print('잘못된 입력입니다 다시 입력해주세요')
                #4
                elif key_return == 52:
                    while True :
                        print('4. 진로변경위반이 맞습니까?')
                        key_return = cv2.waitKey(0)
                        if key_return == 13:
                            self.violation[5] = 4
                            self.csv_datafile.writerow(self.violation)
                            print('등록이 완료되었습니다')
                            self.state = 'end'
                            return
                        elif key_return == 127:
                            print('다시 입력해주세요')
                            break
                        print('잘못된 입력입니다 다시 입력해주세요')
                #5
                elif key_return == 53:
                    while True :
                        print('2. 제차조작신호불이행 위반이 맞습니까?')
                        key_return = cv2.waitKey(0)
                        if key_return == 13:
                            self.violation[5] = 5
                            self.csv_datafile.writerow(self.violation)
                            print('등록이 완료되었습니다')
                            self.state = 'end'
                            return
                        elif key_return == 127:
                            print('다시 입력해주세요')
                            break
                        print('잘못된 입력입니다 다시 입력해주세요')
                else:
                    print('잘못된 입력입니다 다시 입력해주세요')

        
    # TODO 중간사항 저장하고 END
    def finish(self):

        cv2.destroyAllWindows()
        exit()
        pass
        
        
        
        
        
        
        
        
        
        
        
if __name__ =='__main__':

        
    #영상이 들어있는 폴더의 path를 넣어주세요
    video_path = sys.argv[1]

    # path 존재하는지 확인
    if os.path.exists(video_path) == False:
        print('path를 찾을 수 없습니다.\n다시 확인 해주세요')
        exit()

    label = Video_labeling(video_path)

    while True:
        state = label.visualrize()
        
        if state == False:
            break

    
    




