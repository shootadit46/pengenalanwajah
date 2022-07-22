import csv
import datetime
import json
import os
import shutil
import time
import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk
from optparse import Values
from textwrap import fill
from tkinter import *
from tkinter import Message, Text

import cv2
import numpy as np
import pandas as pd
import qrcode
import requests
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from openpyxl import Workbook
from PIL import Image, ImageTk
from xlrd import open_workbook
from xlutils.copy import copy

from Google import Create_Service

window = tk.Tk()
window.title("Menu Aplikasi")
dialog_title = "QUIT"
dialog_text = "Are you sure?"
window.geometry("1920x1080")
window.configure(background="#D1B48C")
bgw = PhotoImage(file="background/sand.png")
backround_label = Label(window, image=bgw)
backround_label.place(x=0, y=0, relwidth=1, relheight=1)
window.attributes("-fullscreen", True)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata

        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    npms = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert("L")
        imageNp = np.array(pilImage, "uint8")
        npm = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        npms.append(npm)
    return faces, npms


def Absen():
    newWindow4 = Toplevel()

    message = tk.Label(
        newWindow4,
        text="Absensi Pendeteksi Wajah",
        bg="#D1B48C",
        fg="#222831",
        width=35,
        height=3,
        font=("Comic Sans MS", 30, "bold"),
    )
    message.place(x=220, y=50)

    lbl5 = tk.Label(
        newWindow4,
        text="Masukan MatKul :",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl5.place(x=285, y=210)

    txt5 = tk.Entry(newWindow4, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt5.place(x=510, y=225)

    lbl6 = tk.Label(
        newWindow4,
        text="Masukan Dosen :",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl6.place(x=290, y=270)

    txt6 = tk.Entry(newWindow4, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt6.place(x=510, y=285)

    lbl7 = tk.Label(
        newWindow4,
        text="Masukan Kelas :",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl7.place(x=295, y=330)

    txt7 = tk.Entry(newWindow4, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt7.place(x=510, y=345)

    def clear4():
        txt5.delete(0, "end")
        res = ""
        # message.configure(text=res)

    def clear5():
        txt6.delete(0, "end")
        res = ""
        # message.configure(text=res)

    def clear6():
        txt7.delete(0, "end")
        res = ""
        # message.configure(text=res)

    def lihatDataAbsen():
        kelass = str([txt7.get()])
        matkul = str([txt5.get()])
        newWindow2 = Tk()
        frm2 = tk.LabelFrame(
            newWindow2,
            text=["Data Absensi Mahasiswa Mata Kuliah " + matkul + " Kelas " + kelass],
            font=("Comic Sans MS", 15, " bold "),
        )
        frm2.place(height=600, width=1250)
        # frm.pack(side=tk.LEFT, padx=20)

        tv2 = ttk.Treeview(frm2)
        tv2.place(relheight=5, relwidth=1)

        treescrolly = tk.Scrollbar(frm2, orient="vertical", command=tv2.yview)
        treescrollx = tk.Scrollbar(frm2, orient="horizontal", command=tv2.xview)
        tv2.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")

        df = pd.read_excel("Attendance\Absen" + "-" + matkul + ".xlsx")
        tv2["column"] = list(df.columns)
        tv2["show"] = "headings"
        for column in tv2["columns"]:
            tv2.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        for row in df_rows:
            tv2.insert("", "end", values=row)

        quitWindow = tk.Button(
            newWindow2,
            text="Tutup",
            command=newWindow2.destroy,
            fg="#eeeeee",
            bg="#0D6EFD",
            width=14,
            height=1,
            activebackground="#11468F",
            activeforeground="white",
            font=("Comic Sans MS", 12, " bold "),
        )
        quitWindow.place(x=500, y=650)
        newWindow2.attributes("-fullscreen", True)

        newWindow2.configure(background="#D1B48C")
        newWindow2.title("Catatan Kehadiran")
        newWindow2.geometry("1300x500")
        newWindow2.mainloop()

    def TrackImages():
        matkul = str([txt5.get()])
        dosen = str([txt6.get()])
        recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
        recognizer.read("TrainingImageLabel\Trainner.yml")
        harcascadePath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath)
        df = pd.read_csv("StudentDetails\DaftarMahasiswa.csv")
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ["NPM", "Nama", "Kelas", "Mata Kuliah", "Dosen", "Tanggal", "Waktu"]
        attendance = pd.DataFrame(columns=col_names)
        while True:
            ret, im = cam.read()
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
                npm, conf = recognizer.predict(gray[y : y + h, x : x + w])
                if conf < 50:
                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    aa = df.loc[df["NPM"] == npm]["Nama"].values
                    bb = df.loc[df["NPM"] == npm]["Kelas"].values
                    tt = str(npm) + "-" + str(aa) + "-" + str(bb)
                    attendance.loc[len(attendance)] = [npm, aa, bb, matkul, dosen, date, timeStamp]
                else:
                    npm = "Tidak Diketahui"
                    tt = str(npm)
                if conf > 75:
                    noOfFile = len(os.listdir("ImagesUnknown")) + 1
                    cv2.imwrite("ImagesUnknown\Image" + str(noOfFile) + ".jpg", im[y : y + h, x : x + w])
                cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)
            attendance = attendance.drop_duplicates(subset=["NPM"], keep="first")
            cv2.putText(im, "Tekan F untuk selesai", (170, 470), font, 1, (0, 255, 0), 2)
            cv2.imshow("Proses Absensi", im)
            if cv2.waitKey(1) == ord("f"):
                break
        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
        Hour, Minute, Second = timeStamp.split(":")
        fileName = "Attendance\Absen" + "-" + matkul + ".xlsx"
        attendance.to_excel(fileName, sheet_name=date, index_label="‎", columns=None, na_rep="")
        # fileName="Attendance\Absen"+"_"+date+"_"+Hour+"-"+Minute+"-"+Second+".xlsx"
        # fileName.to_excel('"Absen"+date+"_"+Hour+"-"+Minute+"-"+Second.xlsx', index=False, sheet_name='aye1')
        # attendance.to_csv(fileName, index=False, sheet_name=date)
        # df = pd.read_csv("Attendance\Absen" + "-" + matkul + ".csv")
        # excelWriter = pd.ExcelWriter("Attendance\Absen" + "-" + matkul + ".xlsx")
        # df.to_excel(excelWriter, index=False)
        # excelWriter.save()
        cam.release()
        cv2.destroyAllWindows()
        # print(attendance)
        res = attendance

        # message2.configure(text=res)

    def Download():
        # googleapiv3
        matkul = str([txt5.get()])
        CLIENT_SECRET_FILE = "client_secret_GoogleCloudDemo.json"
        API_NAME = "drive"
        API_VERSION = "v3"
        SCOPES = ["https://www.googleapis.com/auth/drive.file"]

        service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
        folder_id = "1DCImExo6_-Ai6f_Ev4xP5qW1wppyYJqU"
        file_names = ["Absen" + "-" + matkul + ".xlsx"]
        mime_types = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

        for file_name, mime_type in zip(file_names, mime_types):
            file_metadata = {"name": file_name, "parents": [folder_id]}
            # media = MediaFileUpload('./Attendance/{0}'.format(file_name), mimetype=mime_type)
            media = MediaFileUpload("./Attendance/{0}".format(file_name), mimetype=mime_type)
            service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # qrcode
        link = "https://drive.google.com/drive/u/1/folders/1DCImExo6_-Ai6f_Ev4xP5qW1wppyYJqU"
        x = qrcode.make(link)
        x.save("absen.jpeg")
        qr = PhotoImage(file="Absenn.png")
        qr2 = Label(newWindow4, image=qr, width=180, height=190)
        qr2.place(x=725, y=490)
        # qr2.grid(row=800,column=200)
        newWindow4.mainloop()

    clearButton4 = tk.Button(
        newWindow4,
        command=clear4,
        text="Hapus",
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=1,
        cursor="hand2",
        activebackground="#FF1818",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )

    clearButton4.place(x=890, y=222)

    # tombol hapus dosen
    clearButton5 = tk.Button(
        newWindow4,
        text="Hapus",
        command=clear5,
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=1,
        cursor="hand2",
        activebackground="#FF1818",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    clearButton5.place(x=890, y=282)

    # tombol hapus kelas absensi
    clearButton6 = tk.Button(
        newWindow4,
        text="Hapus",
        command=clear6,
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=1,
        cursor="hand2",
        activebackground="#B20600",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    clearButton6.place(x=890, y=342)

    trackImg = tk.Button(
        newWindow4,
        text="Scan Wajah",
        command=TrackImages,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    trackImg.place(x=400, y=430)

    lihatdataabsen = tk.Button(
        newWindow4,
        text="Lihat Absensi",
        command=lihatDataAbsen,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    lihatdataabsen.place(x=570, y=430)

    quitWindow = tk.Button(
        newWindow4,
        text="Keluar",
        command=newWindow4.destroy,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    quitWindow.place(x=400, y=510)

    downloadAbsensi = tk.Button(
        newWindow4,
        text="Download Absensi",
        command=Download,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    downloadAbsensi.place(x=760, y=430)

    # pendaftaran = tk.Button(
    #     newWindow4,
    #     text="Daftar Wajah",
    #     command=Pendaftaran,
    #     fg="#eeeeee",
    #     bg="#0D6EFD",
    #     width=14,
    #     cursor="hand2",
    #     height=1,
    #     activebackground="#11468F",
    #     activeforeground="white",
    #     font=("Comic Sans MS", 12, " bold "),
    # )
    # pendaftaran.place(x=400, y=510)

    # ug = PhotoImage(
    #     file="background/gundar.png",
    # )
    # ugm = Label(window, image=ug)
    # ugm.place(x=120, y=130)

    tutor = tk.Button(
        newWindow4,
        text="Tata Cara Absensi",
        fg="#222831",
        bg="#D1B48C",
        width=25,
        bd=0,
        height=1,
        command=TutorialAbsen,
        activebackground="#D1B48C",
        cursor="hand2",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutor.place(x=0, y=680)

    author = tk.Label(
        newWindow4,
        text="Build by Aditya Pramudita",
        width=20,
        height=1,
        fg="#D82148",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    author.place(x=1050, y=680)

    newWindow4.attributes("-fullscreen", True)
    newWindow4.configure(background="#D1B48C")
    newWindow4.title("Absensi")
    newWindow4.geometry("1920x1080")
    newWindow4.mainloop()


def Pendaftaran():
    newWindow3 = Tk()
    message2 = tk.Label(
        newWindow3,
        text="Pendaftaran Pendeteksi Wajah",
        bg="#D1B48C",
        fg="#222831",
        width=35,
        height=3,
        font=("Comic Sans MS", 30, "bold"),
    )
    message2.place(x=220, y=50)

    lbl = tk.Label(
        newWindow3,
        text="Masukan NPM :",
        width=20,
        height=2,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl.place(x=295, y=210)

    txt = tk.Entry(newWindow3, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt.place(x=510, y=225)

    lbl2 = tk.Label(
        newWindow3,
        text="Masukan Nama :",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl2.place(x=290, y=270)

    txt2 = tk.Entry(newWindow3, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt2.place(x=510, y=285)

    lbl4 = tk.Label(
        newWindow3,
        text="Masukan Kelas :",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl4.place(x=295, y=330)

    txt4 = tk.Entry(newWindow3, width=30, bg="#EEEEEE", fg="#222831", font=("Comic Sans MS", 15, " bold "))
    txt4.place(x=510, y=345)

    lbl3 = tk.Label(
        newWindow3,
        text="Notifikasi : ",
        width=20,
        fg="#222831",
        bg="#D1B48C",
        height=2,
        font=("Comic Sans MS", 15, " bold "),
    )
    lbl3.place(x=320, y=390)
    message = tk.Label(
        newWindow3,
        text="",
        bg="#EEEEEE",
        fg="#222831",
        width=33,
        height=2,
        activebackground="yellow",
        font=("Comic Sans MS", 15, " bold "),
    )
    message.place(x=510, y=405)

    def clear():
        txt.delete(0, "end")
        res = ""
        message.configure(text=res)

    def clear2():
        txt2.delete(0, "end")
        res = ""
        message.configure(text=res)

    def clear3():
        txt4.delete(0, "end")
        res = ""
        message.configure(text=res)

    def TakeImages():
        npm = txt.get()
        name = txt2.get()
        kelas = txt4.get()
        if is_number(npm) and name.isalpha() and kelas.isalnum():
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            # cv2.namedWindow(newWindow3, cv2.WND_PROP_FULLSCREEN)
            # cv2.setWindowProperty(newWindow3, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            harcascadePath = "haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            sampleNum = 0
            font = cv2.FONT_HERSHEY_SIMPLEX
            while True:
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sampleNum = sampleNum + 1
                    cv2.imwrite(
                        "TrainingImage\ " + name + "." + npm + "." + kelas + "." + str(sampleNum) + ".jpg",
                        gray[y : y + h, x : x + w],
                    )
                    cv2.putText(img, "Mohon tunggu sebentar", (160, 470), font, 1, (0, 255, 0), 2)
                    cv2.imshow("Proses Scanning", img)
                if cv2.waitKey(100) & 0xFF == ord("f"):
                    break
                elif sampleNum > 60:
                    break
            cam.release()
            cv2.destroyAllWindows()
            res = name + " Berhasil didaftarkan"
            index = 1
            row = [npm, name, kelas]
            # col_names = ["NPM", "Nama", "Kelas"]
            # datamhs = pd.DataFrame([npm, name, kelas], columns=col_names)
            # writer = pd.ExcelWriter("StudentDetails\path_to_file.xlsx", mode="a", engine="xlsxwriter")
            # datamhs.to_excel(writer)
            # writer.save()

            # datamhs.loc[len(datamhs)] = [index, npm, name, kelas]
            # fileName = "StudentDetails\DaftarMahasiswa.xlsx"
            # datamhs.to_excel(fileName, sheet_name=kelas, index_label="‎", columns=None, na_rep="")

            with open("StudentDetails\DaftarMahasiswa.csv", "a+") as csvFile:
                # fieldnames = ["NPM", "Nama", "Kelas"]
                writer = csv.writer(csvFile)
                # writer.writerow(["index", "NPM", "Nama", "Kelas"])
                # writer.writerow(fieldnames)
                # writer.writeheader()
                writer.writerow(row)
            # index += 1
            csvFile.close()
            message.configure(text=res)

            # tambahain di index 0 text kosong
            df = pd.read_csv("StudentDetails\DaftarMahasiswa.csv")
            excelWriter = pd.ExcelWriter("StudentDetails\DaftarMahasiswa.xlsx")
            df.to_excel(excelWriter, index_label="‎")
            excelWriter.save()
        else:
            if is_number(npm):
                res = "Mohon jangan menggunakan huruf"
                message.configure(text=res)
            if name.isalpha():
                res = "Mohon Masukan Kelas"
                message.configure(text=res)
            if kelas.isalnum():
                res = "Mohon jangan menggunakan spasi dan huruf"
                message.configure(text=res)

    # proses
    def TrainImages():
        recognizer = (
            cv2.face_LBPHFaceRecognizer.create()
        )  # recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        faces, npm = getImagesAndLabels("TrainingImage")
        recognizer.train(faces, np.array(npm))
        recognizer.save("TrainingImageLabel\Trainner.yml")
        res = "Proses Selesai"  # +",".join(str(f) for f in Id)
        message.configure(text=res)

    # datamhs
    def lihatDataMhs():
        newWindow = Tk()
        frm = tk.LabelFrame(newWindow, text="Data Mahasiswa", font=("Comic Sans MS", 15, " bold "))
        frm.place(height=700, width=850)
        # frm.pack(side=tk.LEFT, padx=200)

        tv1 = ttk.Treeview(frm)
        tv1.place(relheight=5, relwidth=1)

        treescrolly = tk.Scrollbar(frm, orient="vertical", command=tv1.yview)
        treescrollx = tk.Scrollbar(frm, orient="horizontal", command=tv1.xview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")

        df = pd.read_excel("StudentDetails\DaftarMahasiswa.xlsx")
        tv1["column"] = list(df.columns)
        tv1["show"] = "headings"

        for column in tv1["columns"]:
            tv1.heading(column, text=column)

        df_rows = df.to_numpy().tolist()
        # df["‎"] = df["npm"] = df["kelas"]
        for row in df_rows:
            tv1.insert("", "end", values=row)

        quitWindow = tk.Button(
            newWindow,
            text="Tutup",
            command=newWindow.destroy,
            fg="#eeeeee",
            bg="#0D6EFD",
            width=14,
            height=1,
            cursor="hand2",
            activebackground="#11468F",
            activeforeground="white",
            font=("Comic Sans MS", 12, " bold "),
        )
        quitWindow.place(x=900, y=50)

        newWindow.attributes("-fullscreen", True)
        newWindow.configure(background="#D1B48C")
        newWindow.title("Data Mahasiswa")
        newWindow.geometry("1920x1080")
        newWindow.mainloop()

    # btn
    clearButton = tk.Button(
        newWindow3,
        text="Hapus",
        command=clear,
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=0,
        cursor="hand2",
        activebackground="#FF1818",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    clearButton.place(x=890, y=222)
    clearButton2 = tk.Button(
        newWindow3,
        text="Hapus",
        command=clear2,
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=1,
        cursor="hand2",
        activebackground="#FF1818",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    clearButton2.place(x=890, y=282)
    clearButton3 = tk.Button(
        newWindow3,
        text="Hapus",
        command=clear3,
        fg="#eeeeee",
        bg="#CF3241",
        width=7,
        height=1,
        cursor="hand2",
        activebackground="#FF1818",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    clearButton3.place(x=890, y=342)

    takeImg = tk.Button(
        newWindow3,
        text="Daftar Wajah",
        command=TakeImages,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    takeImg.place(x=510, y=510)

    trainImg = tk.Button(
        newWindow3,
        text="Proses Wajah",
        command=TrainImages,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    trainImg.place(x=690, y=510)

    lihatdatamhs = tk.Button(
        newWindow3,
        text="Lihat Data MHS",
        command=lihatDataMhs,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    lihatdatamhs.place(x=510, y=580)

    quitWindow = tk.Button(
        newWindow3,
        text="Keluar",
        command=newWindow3.destroy,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    quitWindow.place(x=690, y=580)

    author = tk.Label(
        newWindow3,
        text="Build by Aditya Pramudita",
        width=20,
        height=1,
        fg="#D82148",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    author.place(x=1050, y=680)

    tutor = tk.Button(
        newWindow3,
        text="Tata Cara Pendaftaran",
        fg="#222831",
        bg="#D1B48C",
        width=25,
        bd=0,
        height=1,
        command=TutorialDaftar,
        cursor="hand2",
        activebackground="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutor.place(x=0, y=680)

    newWindow3.attributes("-fullscreen", True)

    newWindow3.configure(background="#D1B48C")
    newWindow3.title("Catatan Kehadiran")
    newWindow3.geometry("1300x500")
    newWindow3.mainloop()


def TutorialDaftar():
    windowDaftar = Tk()
    message2 = tk.Label(
        windowDaftar,
        text="Tata Cara Pendaftaran Wajah",
        bg="#D1B48C",
        fg="#222831",
        width=35,
        height=3,
        font=("Comic Sans MS", 30, "bold"),
    )
    message2.place(x=220, y=50)

    tutorDaftar = tk.Label(
        windowDaftar,
        text="1. Pada Halaman Pendaftaran silahkan Masukan NPM, Nama dan Kelas \nMahasiswa pada Form Pendaftaran.",
        width=70,
        height=2,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )

    tutorDaftar.place(x=300, y=230)

    tutorDaftar2 = tk.Label(
        windowDaftar,
        text="2. Selanjutnya kalian bisa menekan tombol Daftar Wajah untuk         \nmelakukan Scanning kemudian tunggu hingga proses scanning selesai.",
        width=70,
        height=2,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorDaftar2.place(x=300, y=300)

    tutorDaftar3 = tk.Label(
        windowDaftar,
        text="3. Pastikan pada saat Scanning Wajah berada ditempat yang terang   \nagar mendapatkan hasil yang sempurna pada saat melakukan absensi.",
        width=70,
        height=2,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorDaftar3.place(x=300, y=370)

    tutorDaftar4 = tk.Label(
        windowDaftar,
        text="4. Jika sudah maka kalian bisa menekan tombol Proses Wajah untuk    \nmemproses wajah kalian kedalam database maka akan muncul notifikasi\nProses Selesai.",
        width=70,
        height=3,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorDaftar4.place(x=300, y=440)

    tutorDaftar5 = tk.Label(
        windowDaftar,
        text="5. Jika Pendaftaran Wajah sudah selesai, silahkan dicek apakah data  \nsudah terdaftar atau belum, kalian bisa melihat dengan menekan \ntombol Lihat Data Mahasiswa.",
        width=70,
        height=3,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorDaftar5.place(x=300, y=530)

    # tutorDaftar6 = tk.Label(
    #     windowDaftar,
    #     text="5. Untuk Pendaftaran Wajah sudah selesai, silahkan dicek apakah data \nsudah masuk kedalam database  kalian bisa menekan tombol Lihat Data \nMahasiswa.",
    #     width=70,
    #     height=3,
    #     justify=LEFT,
    #     fg="#222831",
    #     bg="#D1B48C",
    #     font=("Comic Sans MS", 12, " bold "),
    # )
    # tutorDaftar6.place(x=300, y=530)

    quitWindow = tk.Button(
        windowDaftar,
        text="Tutup",
        command=windowDaftar.destroy,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    quitWindow.place(x=760, y=620)

    author = tk.Label(
        windowDaftar,
        text="Build by Aditya Pramudita",
        width=20,
        height=1,
        fg="#D82148",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    author.place(x=1050, y=680)

    windowDaftar.attributes("-fullscreen", True)
    windowDaftar.configure(background="#D1B48C")
    windowDaftar.title("Tutorial")
    windowDaftar.geometry("1920x1080")
    windowDaftar.mainloop()


def TutorialAbsen():
    windowAbsen = Tk()
    message2 = tk.Label(
        windowAbsen,
        text="Tata Cara Absensi Wajah",
        bg="#D1B48C",
        fg="#222831",
        width=35,
        height=3,
        font=("Comic Sans MS", 30, "bold"),
    )
    message2.place(x=220, y=50)

    tutorAbsen = tk.Label(
        windowAbsen,
        text="1. Pertama-tama jika kalian belum pernah mendaftar pada aplikasi ini, \ndiwajibkan mendaftar terlebih dahulu di Halaman Pendaftaran.",
        width=70,
        height=2,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )

    tutorAbsen.place(x=300, y=200)

    tutorAbsen2 = tk.Label(
        windowAbsen,
        text="2. Pada Halaman Absensi Masukan Mata Kuliah, Nama Dosen dan Nama \nKelas Utama yang ingin diabsen kalian pada Form Pendaftaran.",
        width=70,
        height=2,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorAbsen2.place(x=300, y=270)

    tutorAbsen3 = tk.Label(
        windowAbsen,
        text="3. Selanjutnya kalian bisa menekan tombol Scan Wajah untuk memulai   \nabsensi mahasiswa, Pastikan semua wajah mahasiswa pada saat scan \nmuncul NPM, nama  dan kelas pada wajah mereka.",
        width=70,
        height=3,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorAbsen3.place(x=300, y=340)

    tutorAbsen4 = tk.Label(
        windowAbsen,
        text="4. Jika semua mahasiswa sudah melakukan scan absensi, selanjutnya    \nuntuk mengehentikan proses Scan absensi bisa menekan tombol Q \npada Keyboard.",
        width=70,
        height=3,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorAbsen4.place(x=300, y=430)

    tutorAbsen5 = tk.Label(
        windowAbsen,
        text="5. Jika proses Absensi sudah selesai maka data absensi bisa dilihat    \npada tabel mahasiswa dengan menekan tombol Lihat Data Absen dan \nuntuk dosen yang ingin mendownload data absen bisa menekan tombol \nDownload.",
        width=70,
        height=4,
        justify=LEFT,
        fg="#222831",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    tutorAbsen5.place(x=300, y=520)

    quitWindow = tk.Button(
        windowAbsen,
        text="Tutup",
        command=windowAbsen.destroy,
        fg="#eeeeee",
        bg="#0D6EFD",
        width=14,
        height=1,
        cursor="hand2",
        activebackground="#11468F",
        activeforeground="white",
        font=("Comic Sans MS", 12, " bold "),
    )
    quitWindow.place(x=760, y=620)

    author = tk.Label(
        windowAbsen,
        text="Build by Aditya Pramudita",
        width=20,
        height=1,
        fg="#D82148",
        bg="#D1B48C",
        font=("Comic Sans MS", 12, " bold "),
    )
    author.place(x=1050, y=680)

    windowAbsen.attributes("-fullscreen", True)
    windowAbsen.configure(background="#D1B48C")
    windowAbsen.title("Tutorial")
    windowAbsen.geometry("1920x1080")
    windowAbsen.mainloop()


judul = tk.Label(
    window,
    text="Aplikasi Absensi Pendeteksi Wajah",
    bg="#D1B48C",
    fg="#222831",
    width=35,
    height=3,
    font=("Comic Sans MS", 30, "bold"),
)
judul.place(x=220, y=0)

linkdaftar = tk.Button(
    window,
    text="Pendaftaran",
    command=Pendaftaran,
    fg="#eeeeee",
    bg="#0D6EFD",
    width=14,
    height=1,
    cursor="hand2",
    activebackground="#11468F",
    activeforeground="white",
    font=("Comic Sans MS", 12, " bold "),
)
linkdaftar.place(x=430, y=510)

linkabsen = tk.Button(
    window,
    text="Absensi",
    command=Absen,
    fg="#eeeeee",
    bg="#0D6EFD",
    width=14,
    height=1,
    cursor="hand2",
    activebackground="#11468F",
    activeforeground="white",
    font=("Comic Sans MS", 12, " bold "),
)
linkabsen.place(x=700, y=510)

quitWindow = tk.Button(
    window,
    text="Keluar",
    command=window.destroy,
    fg="#eeeeee",
    bg="#0D6EFD",
    width=14,
    height=1,
    cursor="hand2",
    activebackground="#11468F",
    activeforeground="white",
    font=("Comic Sans MS", 12, " bold "),
)
quitWindow.place(x=565, y=600)

author = tk.Label(
    window,
    text="Build by Aditya Pramudita",
    width=20,
    height=1,
    fg="#D82148",
    bg="#D1B48C",
    font=("Comic Sans MS", 12, " bold "),
)
author.place(x=1050, y=680)

menu = PhotoImage(file="face.png")
menuu = Label(window, image=menu, width=650, height=350)
menuu.place(x=320, y=130)

copyWrite = tk.Text(
    window, background=window.cget("background"), borderwidth=0, font=("Comic Sans MS", 30, "italic bold underline")
)
copyWrite.tag_configure("superscript", offset=10)
copyWrite.insert(
    "insert",
    "Developed by Aditya",
)
copyWrite.configure(state="disabled", fg="red")
copyWrite.pack(side="left")
copyWrite.place(x=800, y=750)

window.mainloop()
