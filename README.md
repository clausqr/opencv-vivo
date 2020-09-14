# OpenCV-Vivo with numpy

Playground editor for python OpenCV code applying results on the images live as you type.

It is very often the case that you need to tune your OpenCV pipeline, from changing the kernel size of your first Gaussian blur filter to much more finer and complicated parameters. If this pipeline is in the middle of a more complex problem, it may be difficult to quickly tune. Other methods like jupyter notebooks exist, but they require you to write some boilerplate code each time, think about where the sample images are and how to load them, and hitting CTRL-ENTER infinity of times.

I wrote this to avoid that!

## What you get
1. An editor where you can type your OpenCV + numpy code. 
2. In this editor, you already have your pasted image in the variables `src`, and a copy in `img` (like in most of OpenCV's docs). Put your results in the `dst` variable to see it live.
3. 2 extra windows, one to show the pasted image and other one to show live the contents of the `dst` variable, which you can modify and break without anything wrong happening. 
4. Buttons to paste the image, copy the text, copy the results, and the most useful one: "Autograb", which does just that: graps your last copied image and runs it through your code, showing you the result live.
5. An extra variable `msg` to show text messages in the statusbar of the output image window.

## What's in it
Editor comes preloaded with OpenCV and numpy, but you can additionally import anything you want to. The code you type in the editor gets compiled to a function object using Python's `compile`. Before that, the local dictionary passed to compile is populated with the `img` and `src` variables, numpy and OpenCV and nothing else. Then, the compiled function object is executed, and the results from `dst` and `msg` are extracted and shown. The execution is guarded by `try` - `except` blocks so that you can type invalid code, divide by 0, etc. and nothing bad will happen, just correct it and as soon as the contents of `dst` have the appearance of an image again, they will be shown in its window.

This is a work in progress, please use the issues section to report problems or request features.

## Getting Started



 