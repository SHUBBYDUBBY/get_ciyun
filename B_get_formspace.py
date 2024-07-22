from selenium import webdriver  
import tkinter as tk  
from tkinter import filedialog, messagebox, StringVar, Entry, Label, Button 
import requests
from tqdm import tqdm
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from selenium.webdriver.chrome.service import Service
import re
import wordcloud
import jieba
from chinese_stopword import chinese_stopwords
import os
import matplotlib.pyplot as plt

path =  Service('chromedriver.exe')
browser = webdriver.Chrome(service=path)    

class URL:
    def __init__(self,url_inde):
        self.url = url_inde
    # !该输入url为一个视频空间URL

    def danmuku_url_lists_get_def (self):
    # *输入一个up主的个人空间的url，得到该空间的全部视频urls【list】
    # *遍历该【list】，输出弹幕文本的urls【list】(格式是api.blbl.com...)
        browser.get(self.url)  
        try:  
            element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "some_element_id"))  )  
        except Exception as e:  
            print(e)  
        source_code = browser.page_source  
        live_urls = re.findall(r'<a href="(//www\.bilibili\.com/video/[^"]+)"',source_code)
        # print(live_urls)
        unique_urls = list(set(live_urls))
        iblbl_url_lists = [url.replace("//www.bilibili.com", "https://www.ibilibili.com") for url in unique_urls]
        danmuku_urls = [] 
        for iblbl_url_list in iblbl_url_lists:
            getheaders = {
                "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
                }
            resp = requests.get(iblbl_url_list,headers=getheaders)
            resp.encoding = "utf-8"
            # https://www.bilibili.com/video/BV1Ay411i7xE/?spm_id_from=333.999.0.0
            # https://api.bilibili.com/x/v1/dm/list.so?oid=1614845667
            danmuku_url_text = re.findall(r'https://api\.bilibili\.com/x/v1/dm/list\.so\?oid=\d+',resp.text)
            danmuku_urls.extend(danmuku_url_text)
        danmuku_urls = list(set(danmuku_urls)) 
        return danmuku_urls

class vtuber:
    def __init__(self,vtuber_name_inde,pic_inde,save_path_inde):
        self.name = vtuber_name_inde
        self.pic = pic_inde
        self.path = save_path_inde
    # *名字，图片，保存路径

    def wc_set (self):
        # *输入一个图片路径用于渲染图片颜色
        # *输出一个wc,用于之后渲染
        vtuber_pics = plt.imread(self.pic)
        color_generator=wordcloud.ImageColorGenerator(vtuber_pics)
        w_seting = wordcloud.WordCloud(
        font_path="C:\Windows\Fonts\simhei.ttf",
        stopwords= chinese_stopwords,
        background_color='white',
        color_func=color_generator,
        mask=vtuber_pics)
        return w_seting

        

    def danmuku_get (self,url_list_inde):
    # *输入一组api.blbl.com的弹幕文本url
    # *把输入的url都集合在一个库中
    # *输出库

        danmuku_all = ""
        for ii in url_list_inde :
            getheaders = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0" }
            resp = requests.get(ii,headers=getheaders)
            resp.encoding = "utf-8"
            danmu_list = re.findall(r'<d p=".*?">(.*?)</d>',resp.text)
            danmuku = '\n'.join(danmu_list)
            danmuku_all += danmuku + '\n'
        danmuku_all =' '.join(jieba.lcut( danmuku_all))
        return danmuku_all
        
    def pnggenerate (self,danmuku_inde,wc):
        # *输入wc和弹幕库
        # *生成w_seting图片

        wc.generate(danmuku_inde)
        file_path = os.path.join(self.path, f"{self.name}_wordcloud.png")  
        os.makedirs(self.path, exist_ok=True)  
        wc.to_file(file_path)

class TKget:  
    def __init__(self, root_inde):  
        self.root = root_inde  
        self.root.title("词云生成工具")  
        self.pic_path = None  
        self.savefolder_path = None  
        self.vtuber_name = StringVar()
        self.url = StringVar()
        self.setup_ui()  
  
    def setup_ui(self):  
        # Label: 请输入vtuber名字  
        Label(self.root, text="请输入vtuber名字：").pack(pady=10) 
        Entry(self.root, textvariable=self.vtuber_name).pack(pady=5)

        Label(self.root, text="请输入vtuber视频空间URL：").pack(pady=10)
        Entry(self.root, textvariable=self.url).pack(pady=5)
  
        Button(self.root, text="选择图片文件", command=self.select_picpath).pack(pady=10)   
        Button(self.root, text="选择文件夹", command=self.select_folderpath).pack(pady=10)  
        
        Button(self.root, text="提交", command=self.on_submit).pack(pady=20)  
  
    def select_picpath(self):  
        self.pic_path = filedialog.askopenfilename(filetypes=[("All files", "*.*"),("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg") ])  
  
    def select_folderpath(self):  
        self.savefolder_path = filedialog.askdirectory()  
  
    def on_submit(self):  
        if self.pic_path and self.savefolder_path and self.url and self.vtuber_name.get():  
            messagebox.showinfo("提交信息", f"图片文件: {self.pic_path}\n文件夹路径: {self.savefolder_path}\nVTuber名字: {self.vtuber_name.get()}\n{self.url.get()}")
            vtuber_name = self.vtuber_name.get()  
            url = self.url.get()  
            pic_path = self.pic_path
            savefolder_path = self.savefolder_path
            
            url1 = URL(url) 
            vtuber1 = vtuber(vtuber_name,rf"{pic_path}",rf"{savefolder_path}")

            m = url1.danmuku_url_lists_get_def()

            ku = vtuber1.danmuku_get(m)
            w = vtuber1.wc_set()

            vtuber1.pnggenerate(ku,w)

            browser.close()

            self.root.destroy()

        else:  
            messagebox.showerror("错误", "请确保所有字段都已填写！")  
  
def main():  
    root = tk.Tk()  
    app = TKget(root) 
    root.mainloop()  
  
if __name__ == "__main__":  
    main()
