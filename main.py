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

import cv2
import cv2.aruco as aruco

class CamApp(App):

    def build(self):
        self.img1=Image()
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(self.img1)
        #opencv2 stuffs
        self.capture = cv2.VideoCapture(0)

        self.btn_get = Button(text="Take a photo",size_hint =(.2, .2),pos_hint={'x': .1, 'center_y': .9})
        self.btn_show=Button(text="Show system",size_hint =(.2, .2),pos_hint={'x': .4, 'center_y': .9})
        self.btn_reset=Button(text="Cancel",size_hint =(.2, .2),pos_hint={'x': .7, 'center_y': .9})

        self.btn_get.bind(on_press=self.take_photo)
        self.btn_show.bind(on_press=self.give_photo)
        self.btn_show.bind(on_press=self.cancel_pressed)

        self.camera_status="going"

        layout.add_widget(self.btn_get)
        layout.add_widget(self.btn_show)

        cv2.namedWindow("CV2 Image")
        Clock.schedule_interval(self.update, 1.0/33.0)
        return layout

    def update(self, dt):
        # display image from cam in opencv window

        ARUCO_PARAMETERS = aruco.DetectorParameters()
        ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)

        ret, frame = self.capture.read()
        #=====================================
        #test test

        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # cv2.imshow('frame',frame)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(im, ARUCO_DICT, parameters=ARUCO_PARAMETERS)

        if ids is not None:
            print('detected: {}'.format(len(ids)))
            for i, corner in zip(ids, corners):
                # print('ID: {}; Corners: {}'.format(i, corner))
                # print(sum(corner[0, 0, :]) // 4, sum(corner[0, :, 0]) // 4)
                cv2.circle(im, center=(int(sum(corner[0, :, 0]) // 4), int(sum(corner[0, :, 1]) // 4)), radius=5,
                           color=(255, 0, 0))

            im = aruco.drawDetectedMarkers(im, corners, borderColor=(255, 0, 0))

        #=====================================
        cv2.imshow("CV2 Image", frame)
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        if(self.camera_status=='going'):
            texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.img1.texture = texture1

    def take_photo(self,event):
        self.camera_status='stop'

    def cancel_pressed(self,event):
        self.camera_status='going'

    def give_photo(self,event):
        pass

if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()