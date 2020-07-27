for i in  range(10000):
    glob_steps = i
    index = glob_steps%3000
    if index==0:

        print('已保存权重第：',int(0%3000),'版本')
