# from kivymd.app import MDApp
# from kivy.uix.screenmanager import Screen
# from kivy.lang import Builder
#
# KV='''
# MDBoxLayout:
#     orientation: "vertical"
#     md_bg_color: "#1E1E15"
#
#     MDTopAppBar:
#         title: "MDTopAppBar"
#
#     MDLabel:
#         text: "Content"
#         halign: "center"
#
#     MDRectangleFlatButton:
#         text: "Button"
#         pos_hint:{'center_x':0.5, 'center_y':0.1}
# '''
#
# class MainApp(MDApp):
#     def __init__(self):
#         super().__init__()
#         self.theme_cls.theme_style = "Dark"
#         self.theme_cls.primary_palette = "Orange"
#         self.kvs=Builder.load_string(KV)
#
#     def build(self):
#         screen=Screen()
#         screen.add_widget(self.kvs)
#         return screen
#
# ma=MainApp()
# ma.run()

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.relativelayout import RelativeLayout

import cv2
import cv2.aruco as aruco


def overlay_image(src_img,  # оригинальное изображение
                  src_pts,  # координаты маркеров на оригинальном изображении
                  dst_img,  # целевое изображение
                  dst_pts  # координаты маркеров на целевом изображении
                  ):
    orig_h = src_img.shape[0]
    orig_w = src_img.shape[1]

    # выравнивание исходного изображения
    ort_pts = [[0, 0], [0, orig_w - 1], [orig_h - 1, 0], [orig_h - 1, orig_w - 1]]
    print(src_img.type())
    ort_matrix = cv2.getPerspectiveTransform(src_pts, ort_pts)
    ort = cv2.warpPerspective(src_img, ort_matrix, (orig_h, orig_w))

    # наложение выравненного
    dst_matrix = cv2.getPerspectiveTransform(ort_pts, dst_pts)
    dst = cv2.warpPerspective(ort, dst_matrix, (orig_h, orig_w))
    return dst

class CamApp(App):

    def build(self):
        self.ARUCO_PARAMETERS = aruco.DetectorParameters()
        self.ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
        self.img1=Image(pos=(0,0),size_hint_x =1)

        layout = BoxLayout(orientation="vertical")

        rl = RelativeLayout(size=(200, 100))

        layout.add_widget(self.img1)
        #opencv2 stuffs
        self.capture = cv2.VideoCapture(0)

        self.btn_get = Button(text="Take a photo",size_hint =(.15, .2),pos=(0,0))
        self.btn_show=Button(text="Show phooto",size_hint =(.15, .2),pos=(150,0))
        self.btn_addImage=Button(text="add mask",size_hint =(.15, .2),pos=(300,0))
        self.btn_overlay = Button(text="Overlay", size_hint=(.15, .2), pos=(450, 0))
        self.btn_reset=Button(text="Cancel",size_hint =(.15, .2),pos=(600,0))


        self.btn_get.bind(on_press=self.take_photo)
        self.btn_show.bind(on_press=self.give_photo)
        self.btn_addImage.bind(on_press=self.add_mask)
        self.btn_overlay.bind(on_press=self.overlay)
        self.btn_reset.bind(on_press=self.cancel_pressed)

        self.camera_status="going"

        rl.add_widget(self.btn_get)
        rl.add_widget(self.btn_show)
        rl.add_widget(self.btn_addImage)
        rl.add_widget(self.btn_overlay)
        rl.add_widget(self.btn_reset)

        layout.add_widget(rl)

        cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0/33.0)

        ret, frame = self.capture.read()
        self.photo = frame

        self.corners={}

        return layout

    def update(self, dt):
        # display image from cam in opencv window



        ret, frame = self.capture.read()
        #=====================================
        #test test

        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('frame',frame)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(im, self.ARUCO_DICT, parameters=self.ARUCO_PARAMETERS)
        if(self.camera_status=='mask'):

            if ids is not None:
                print('detected: {}'.format(len(ids)))
                for i, corner in zip(ids, corners):
                    # print('ID: {}; Corners: {}'.format(i, corner))
                    # print(sum(corner[0, 0, :]) // 4, sum(corner[0, :, 0]) // 4)
                    cv2.circle(frame, center=(int(sum(corner[0, :, 0]) // 4), int(sum(corner[0, :, 1]) // 4)), radius=5,
                               color=(255, 0, 0), thickness=10)

                im = aruco.drawDetectedMarkers(frame, corners, borderColor=(0, 0, 255))

        #=====================================

        if(self.camera_status=="overlay"):
            if len(self.corners.keys()) == 4:
                self.corners=dict(sorted(self.corners.items()))
                current_corners={}
                if ids is not None:
                    print('detected: {}'.format(len(ids)))
                    for i, corner in zip(ids, corners):
                        current_corners[i[0]] = corner
                    current_corners=dict(sorted(current_corners.items()))
                    print()
                    if len(current_corners.keys()) == 4:
                        frame=overlay_image(self.photo, self.corners.values(),frame,current_corners.values())
            else:
                print(len(self.corners.keys()))

        #=====================================
        cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        if(self.camera_status=='going' or self.camera_status=='mask' or self.camera_status=='overlay'):
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture1

    def take_photo(self,event):
        #self.camera_status='stop'
        ret, frame = self.capture.read()
        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('frame',frame)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(im, self.ARUCO_DICT, parameters=self.ARUCO_PARAMETERS)
        self.corners={}
        if (self.camera_status == 'mask'):

            if ids is not None:
                print('detected: {}'.format(len(ids)))
                for i, corner in zip(ids, corners):
                    #print(i)
                    self.corners[i[0]]=corner
                    print('ID: {}; Corners: {}'.format(i, corner))
                    self
                    # print(sum(corner[0, 0, :]) // 4, sum(corner[0, :, 0]) // 4)
                    cv2.circle(frame, center=(int(sum(corner[0, :, 0]) // 4), int(sum(corner[0, :, 1]) // 4)), radius=5,
                               color=(255, 0, 0), thickness=10)

                im = aruco.drawDetectedMarkers(frame, corners, borderColor=(0, 0, 255))
        self.photo=frame

    def cancel_pressed(self,event):
        self.camera_status='going'
        print(self.corners)

    def give_photo(self,event):
        self.camera_status='stop'
        frame=self.photo
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.img1.texture = texture1

    def add_mask(self,event):
        self.camera_status="mask"

    def overlay(self,event):
        self.camera_status="overlay"


if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()