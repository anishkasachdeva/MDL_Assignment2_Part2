import numpy as np
import os
def display(file,act,h1,a1,s1,ut):
    if act==0:
        f.write("(" + str(h1) + "," + str(a1) + "," + str(s1) + "):" + "SHOOT" + "=[" + str(round(ut,3)) + "]"+"\n")
    elif act==1:
        f.write("(" + str(h1) + "," + str(a1) + "," + str(s1) + "):" + "DODGE" + "=[" + str(round(ut,3)) + "]"+"\n")
    elif act==2:
        f.write("(" + str(h1) + "," + str(a1) + "," + str(s1) + "):" + "RECHARGE" + "=[" + str(round(ut,3)) + "]"+"\n")
    else:
        f.write("(" + str(h1) + "," + str(a1) + "," + str(s1) + "):" + str(act) + "=[" + str(round(ut,3)) + "]"+"\n")

def valid_actions(state1):
    s1 = state1%3
    a1 = (state1//3)%4
    t=1
    if s1 != 0 and a1 != 0:
        t+=2
    if s1 != 0:
        t+=4
    return t

def check(h1,h2,a1,a2,s1,s2,diff_h,diff_a,diff_s):
    if (h1 - h2 == diff_h) and (a1 - a2 == diff_a) and (s1 - s2 == diff_s):
        return 1
    else:
        return 0

def shoot(state1,state2): #returns the probabilty of shooting
    s1 = state1%3
    a1 = (state1//3)%4
    h1 = (state1//12)%5
    s2 = state2%3
    a2 = (state2//3)%4
    h2 = (state2//12)%5
    if valid_actions(state1)!=7:
        return 0
    if (s1-s2)==1 and (a1-a2)==1 and ((h1-h2)==1 or (h1-h2)==0):
        return 0.5
    return 0

def dodge(state1,state2):    #returns the probabilty of dodging
    s1 = state1%3
    a1 = (state1//3)%4
    h1 = (state1//12)%5
    s2 = state2%3
    a2 = (state2//3)%4
    h2 = (state2//12)%5

    if s1==1:
        if s2==0 and a2-a1==1 and h2==h1:
            return 0.8
        if s2==0 and a2==a1 and h2==h1 and a2==3:
            return 1
        if s2==0 and a2==a1 and h2==h1:
            return 0.2
    if s1==2:
        if s2==1 and a2==a1 and h2==h1 and a2==3:
            return 0.8
        if s2==0 and a2==a1 and h2==h1 and a2==3:
            return 0.2
        if s2==1 and a2==a1 and h2==h1 :
            return 0.8*0.2
        if s2==0 and a2==a1 and h2==h1 :
            return 0.2*0.2
        if s2==1 and (a2-a1)==1 and h2==h1 :
            return 0.8*0.8
        if s2==0 and (a2-a1)==1 and h2==h1 :
            return 0.2*0.8
    return 0

def recharge(state1,state2):     #returns the probabilty of recharging
    s1 = state1%3
    a1 = (state1//3)%4
    h1 = (state1//12)%5
    s2 = state2%3
    a2 = (state2//3)%4
    h2 = (state2//12)%5

    if s1==2 and s2==2 and a1==a2 and h1==h2:
        return 1
    if (s2-s1)==1 and a1==a2 and h1==h2:
        return 0.8
    if s1==s2 and a1==a2 and h1==h2:
        return 0.2
    return 0

penalty = -20 #penalty is same as reward
gamma = 0.99
delta = 0.001

shoot_arr = np.zeros((60, 60))
dodge_arr = np.zeros((60, 60))
recharge_arr = np.zeros((60, 60))
reward_arr = np.zeros((60,3))

for i in range (60):
    for j in range (60):
        # round(answer, 2)
        shoot_arr[i][j] = shoot(i,j)  #seee how to write the syntax of indexing in numpy array...i am confused in this
        dodge_arr[i][j] = dodge(i,j)
        recharge_arr[i][j] = recharge(i,j)

for i in range (60):  # for reward whatever has to be done do it 
    for j in range (3):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1 == 1 and j==0 and a1>0 and s1>0:
            reward_arr[i][j] = (penalty+0)*0.5 + (penalty+10)*0.5 # written like this on purpose so that we remember during evaluations why are we getting zero for absorbing states
        else:
            reward_arr[i][j] = penalty

utility_new = np.zeros(60)
utility_old = np.zeros(60) #put values accordingly. I don't know the original utility values
difference = np.zeros(60)


max_difference = float("inf")
it = 0
try:
    os.mkdir("outputs")
except FileExistsError:
    os.rmdir("outputs")
    os.mkdir("outputs")

f = open("outputs/task_1_trace.txt", "w")
while(max_difference > delta):
    f.write("iteration="+str(it) + "\n")
    
    for i in range(60):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1!=0:
            sum_shoot = reward_arr[i][0]
            sum_dodge = reward_arr[i][1]
            sum_recharge = reward_arr[i][2]
            for j in range(60):
                # column 0 = shoot, column 1 = dodge, column 2 = recharge
                sum_shoot += shoot_arr[i][j] * gamma * utility_old[j]
                sum_dodge += dodge_arr[i][j] * gamma * utility_old[j]
                sum_recharge += recharge_arr[i][j] * gamma * utility_old[j]
            allowed_actions=valid_actions(i)
            if allowed_actions==1:
                sum_dodge=float("-inf")
                sum_shoot=float("-inf")
            if allowed_actions==5:
                sum_shoot=float("-inf")
            utility_new[i] = max([sum_shoot,sum_dodge,sum_recharge])
            if utility_new[i] == sum_shoot:
                action = 0
            elif utility_new[i] == sum_dodge:
                action = 1
            elif utility_new[i] == sum_recharge:
                action = 2

            display(f,action,h1,a1,s1,utility_new[i])
        else:
            utility_new[i]=0
            action=-1
            display(f,action,h1,a1,s1,utility_new[i])
        
    for i in range(60):
        difference[i] = abs(utility_old[i] - utility_new[i])
        utility_old[i]=utility_new[i]
    max_difference = max(difference)
    f.write("\n\n")
    it +=1
f.close()
# -------------------------------

f = open("outputs/task_2_part_1_trace.txt", "w")
penalty = -2.5 #penalty is same as reward
gamma = 0.99
delta = 0.001

shoot_arr = np.zeros((60, 60))
dodge_arr = np.zeros((60, 60))
recharge_arr = np.zeros((60, 60))
reward_arr = np.zeros((60,3))

for i in range (60):
    for j in range (60):
        # round(answer, 2)
        shoot_arr[i][j] = shoot(i,j)  #seee how to write the syntax of indexing in numpy array...i am confused in this
        dodge_arr[i][j] = dodge(i,j)
        recharge_arr[i][j] = recharge(i,j)

for i in range (60):  # for reward whatever has to be done do it 
    for j in range (3):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1 == 1 and j==0 and a1>0 and s1>0:
            reward_arr[i][j] = (-0.25+0)*0.5 + (-0.25+10)*0.5 # written like this on purpose so that we remember during evaluations why are we getting zero for absorbing states
        elif j==0:
            reward_arr[i][j] = -0.25
        else:
            reward_arr[i][j] = penalty

utility_new = np.zeros(60)
utility_old = np.zeros(60) #put values accordingly. I don't know the original utility values
difference = np.zeros(60)


max_difference = float("inf")
it = 0
while(max_difference > delta):
    f.write("iteration="+str(it)+"\n")
    
    for i in range(60):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1!=0:
            sum_shoot = reward_arr[i][0]
            sum_dodge = reward_arr[i][1]
            sum_recharge = reward_arr[i][2]
            for j in range(60):
                # column 0 = shoot, column 1 = dodge, column 2 = recharge
                sum_shoot += shoot_arr[i][j] * gamma * utility_old[j]
                sum_dodge += dodge_arr[i][j] * gamma * utility_old[j]
                sum_recharge += recharge_arr[i][j] * gamma * utility_old[j]
            allowed_actions=valid_actions(i)
            if allowed_actions==1:
                sum_dodge=float("-inf")
                sum_shoot=float("-inf")
            if allowed_actions==5:
                sum_shoot=float("-inf")
            utility_new[i] = max([sum_shoot,sum_dodge,sum_recharge])
            if utility_new[i] == sum_shoot:
                action = 0
            elif utility_new[i] == sum_dodge:
                action = 1
            elif utility_new[i] == sum_recharge:
                action = 2

            display(f,action,h1,a1,s1,utility_new[i])
        else:
            utility_new[i]=0
            action=-1
            display(f,action,h1,a1,s1,utility_new[i])
        
    for i in range(60):
        difference[i] = abs(utility_old[i] - utility_new[i])
        utility_old[i]=utility_new[i]
    max_difference = max(difference)
    f.write("\n\n")
    it +=1
f.close()
# -------------------------------
f = open("outputs/task_2_part_2_trace.txt", "w")
penalty = -2.5 #penalty is same as reward
gamma = 0.1
delta = 0.001

shoot_arr = np.zeros((60, 60))
dodge_arr = np.zeros((60, 60))
recharge_arr = np.zeros((60, 60))
reward_arr = np.zeros((60,3))

for i in range (60):
    for j in range (60):
        # round(answer, 2)
        shoot_arr[i][j] = shoot(i,j)  #seee how to write the syntax of indexing in numpy array...i am confused in this
        dodge_arr[i][j] = dodge(i,j)
        recharge_arr[i][j] = recharge(i,j)

for i in range (60):  # for reward whatever has to be done do it 
    for j in range (3):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1 == 1 and j==0 and a1>0 and s1>0:
            reward_arr[i][j] = (penalty+0)*0.5 + (penalty+10)*0.5 # written like this on purpose so that we remember during evaluations why are we getting zero for absorbing states
        else:
            reward_arr[i][j] = penalty

utility_new = np.zeros(60)
utility_old = np.zeros(60) #put values accordingly. I don't know the original utility values
difference = np.zeros(60)


max_difference = float("inf")
it = 0
while(max_difference > delta):
    f.write("iteration="+str(it)+"\n")
    
    for i in range(60):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1!=0:
            sum_shoot = reward_arr[i][0]
            sum_dodge = reward_arr[i][1]
            sum_recharge = reward_arr[i][2]
            for j in range(60):
                # column 0 = shoot, column 1 = dodge, column 2 = recharge
                sum_shoot += shoot_arr[i][j] * gamma * utility_old[j]
                sum_dodge += dodge_arr[i][j] * gamma * utility_old[j]
                sum_recharge += recharge_arr[i][j] * gamma * utility_old[j]
            allowed_actions=valid_actions(i)
            if allowed_actions==1:
                sum_dodge=float("-inf")
                sum_shoot=float("-inf")
            if allowed_actions==5:
                sum_shoot=float("-inf")
            utility_new[i] = max([sum_shoot,sum_dodge,sum_recharge])
            if utility_new[i] == sum_shoot:
                action = 0
            elif utility_new[i] == sum_dodge:
                action = 1
            elif utility_new[i] == sum_recharge:
                action = 2

            display(f,action,h1,a1,s1,utility_new[i])
        else:
            utility_new[i]=0
            action=-1
            display(f,action,h1,a1,s1,utility_new[i])
        
    for i in range(60):
        difference[i] = abs(utility_old[i] - utility_new[i])
        utility_old[i]=utility_new[i]
    max_difference = max(difference)
    f.write("\n\n")
    it +=1
f.close()
    #----------------------------
f = open("outputs/task_2_part_3_trace.txt", "w")
penalty = -2.5 #penalty is same as reward
gamma = 0.1
delta = 1e-10

shoot_arr = np.zeros((60, 60))
dodge_arr = np.zeros((60, 60))
recharge_arr = np.zeros((60, 60))
reward_arr = np.zeros((60,3))

for i in range (60):
    for j in range (60):
        # round(answer, 2)
        shoot_arr[i][j] = shoot(i,j)  #seee how to write the syntax of indexing in numpy array...i am confused in this
        dodge_arr[i][j] = dodge(i,j)
        recharge_arr[i][j] = recharge(i,j)

for i in range (60):  # for reward whatever has to be done do it 
    for j in range (3):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1 == 1 and j==0 and a1>0 and s1>0:
            reward_arr[i][j] = (penalty+0)*0.5 + (penalty+10)*0.5 # written like this on purpose so that we remember during evaluations why are we getting zero for absorbing states
        else:
            reward_arr[i][j] = penalty

utility_new = np.zeros(60)
utility_old = np.zeros(60) #put values accordingly. I don't know the original utility values
difference = np.zeros(60)


max_difference = float("inf")
it = 0
while(max_difference > delta):
    f.write("iteration="+str(it)+"\n")
    
    for i in range(60):
        s1 = i%3
        a1 = (i//3)%4
        h1 = (i//12)%5
        if h1!=0:
            sum_shoot = reward_arr[i][0]
            sum_dodge = reward_arr[i][1]
            sum_recharge = reward_arr[i][2]
            for j in range(60):
                # column 0 = shoot, column 1 = dodge, column 2 = recharge
                sum_shoot += shoot_arr[i][j] * gamma * utility_old[j]
                sum_dodge += dodge_arr[i][j] * gamma * utility_old[j]
                sum_recharge += recharge_arr[i][j] * gamma * utility_old[j]
            allowed_actions=valid_actions(i)
            if allowed_actions==1:
                sum_dodge=float("-inf")
                sum_shoot=float("-inf")
            if allowed_actions==5:
                sum_shoot=float("-inf")
            utility_new[i] = max([sum_shoot,sum_dodge,sum_recharge])
            if utility_new[i] == sum_shoot:
                action = 0
            elif utility_new[i] == sum_dodge:
                action = 1
            elif utility_new[i] == sum_recharge:
                action = 2

            display(f,action,h1,a1,s1,utility_new[i])
        else:
            utility_new[i]=0
            action=-1
            display(f,action,h1,a1,s1,utility_new[i])
        
    for i in range(60):
        difference[i] = abs(utility_old[i] - utility_new[i])
        utility_old[i]=utility_new[i]
    max_difference = max(difference)
    f.write("\n\n")
    it +=1
f.close()