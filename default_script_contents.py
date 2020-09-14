# Lines commented with hashtag+at symbol: #@
# contain s1, s2 s3 and s4 variables,
# which can be adjusted with the sliders above

s1=146 #@
s2=41 #@
s3=116 #@
s4=128 #@

# dst variable will contain destination image:
dst=np.array(src*(s1/255), dtype=np.uint8)

# msg variable will be displayed in status bar of 'dst' window:
msg="Hello! s1={}".format(s1)