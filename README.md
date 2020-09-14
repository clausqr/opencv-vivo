# OpenCV-Vivo with numpy

Playground editor for Python OpenCV + numpy code applying results on the images live as you type.

It is very often the case that you need to tune your OpenCV pipeline, from changing the kernel size of your first Gaussian blur filter to much more finer and complicated parameters. If this pipeline is in the middle of a more complex problem, it may be difficult to quickly tune. Other methods like jupyter notebooks exist, but they require you to write some boilerplate code each time, think about where the sample images are and how to load them, and hitting CTRL-ENTER infinity of times.

I wrote this to avoid that!

## 1. What you get
1. An editor where you can type your OpenCV + numpy code. 
2. In this editor, you already have your pasted image in the variables `src`, and a copy in `img` (like in most of OpenCV's docs). Put your results in the `dst` variable to see it live.
3. 2 extra windows, one to show the pasted image and other one to show live the contents of the `dst` variable, which you can modify and break without anything wrong happening. 
4. Buttons to paste the image, copy the text, copy the results, and the most useful one: "Autograb", which does just that: graps your last copied image and runs it through your code, showing you the result live.
5. An extra variable `msg` to show text messages in the statusbar of the output image window.

## 2. What's in it
Editor comes preloaded with OpenCV and numpy, but you can additionally import anything you want to. The code you type in the editor gets compiled to a function object using Python's `compile`. Before that, the local dictionary passed to compile is populated with the `img` and `src` variables, numpy and OpenCV and nothing else. Then, the compiled function object is executed, and the results from `dst` and `msg` are extracted and shown. The execution is guarded by `try` - `except` blocks so that you can type invalid code, divide by 0, etc. and nothing bad will happen, just correct it and as soon as the contents of `dst` have the appearance of an image again, they will be shown in its window.

This is a work in progress, please use the issues section to report problems or request features.
Next steps:
 1. include profiling information.
 2. include utility functions auto histograms, pyplot, etc.
 3. TBD
 
## 3. Getting Started

![](cut-opencv-vivo.gif)

#### 1. Download it:
```commandline
git clone https://gitlab.com/clausqr/opencv-vivo
cd opencv-vivo
```

#### 2. Rereate Anaconda environment:
```commandline
conda env create --file environment.yaml
```
If you don't use anaconda you will need to install OpenCV, numpy and Pillow using your preferred method.

#### 3. Run it:  
```commandline
conda activate opencv-en-vivo
python opencv-vivo.py
```

#### 4. Use it:
1. Copy a sample image to the clipboard.
2. Click 'Paste'.
3. Write your code, the image you just pasted is in the variable `src`. Put your results into `dst` variable, watch the results live. Also, you can pass text info into `msg` variable, it will be displayed in the status bar of 'dst' window.
4. If you want to test your code against several images, enable 'Autograb' option to avoid clicking 'Paste' each time.

#### 5. To return to your normal prompt:
Deactivate the Anaconda environment:
```commandline
conda deactivate
```

 