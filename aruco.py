import cv2
import cv2.aruco as aruco
import numpy as np
import os
import socket
import math
import time
import glob





def main():

    host, port = "127.0.0.1", 25001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    cap= cv2.VideoCapture(0)
    time.sleep(2)
    cap.set(3,3840)
    cap.set(4,2160)
    status = True

    while True:
        _,frame = cap.read()
        markerSize = 4
        totalMarkers = 250
        imgGray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        key = getattr(aruco,f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
        arucoDict = aruco.Dictionary_get(key)
        arucoParam = aruco.DetectorParameters_create()
        bbox, ids, rejected = aruco.detectMarkers(imgGray,arucoDict, parameters=arucoParam)
        img_counter = 0
        cv2.imshow("result",frame)
        cv2.waitKey(1)


        # cropping using aruco marker 1 and 2
        if ids is not None:
            length_ids = len(ids)
            # aruco.drawDetectedMarkers(frame,bbox)
        if ids is not None and [1] in ids and [2] in ids and [3] in ids and [4] in ids:

            ids_formatted = []
            for i in range(length_ids):
                ids_formatted.append(ids[i][0])

            # find 1 is top left 2 is top right 3 is bottom left 4 is bottom right
            pos1 = ids_formatted.index(1)
            pos2 = ids_formatted.index(2)
            pos3 = ids_formatted.index(3)
            pos4 = ids_formatted.index(4)
            TL1 = bbox[pos1][0][0]
            TR2 = bbox[pos2][0][1]
            BL3 = bbox[pos3][0][3]
            BR4 = bbox[pos4][0][2]

            calibCoordsX = [TL1[0],TR2[0],BL3[0],BR4[0]]
            calibCoordsY = [TL1[1],TR2[1],BL3[1],BR4[1]]
            # minus in front of y coords bc webcam origin flipped in x axis compared to unity origin
            # change these to 950 and 590 stuff



            # calibration
            width, height = 950,590
            pts1 = np.float32([[calibCoordsX[0],calibCoordsY[0]],[calibCoordsX[1],calibCoordsY[1]],[calibCoordsX[2],calibCoordsY[2]],[calibCoordsX[3],calibCoordsY[3]]])
            pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])
            M = cv2.getPerspectiveTransform(pts1,pts2)
            calibframe = cv2.warpPerspective(frame,M,(width,height))
            bbox_c, ids_c, rejected_c = aruco.detectMarkers(calibframe,arucoDict, parameters=arucoParam)
            cv2.imshow('warped',calibframe)
            if status:
                pauseframe = calibframe
                bbox_p, ids_p, rejected_p = aruco.detectMarkers(calibframe,arucoDict, parameters=arucoParam)
                aruco.drawDetectedMarkers(calibframe,bbox_p)
                cv2.imshow('pause frame when in animate',pauseframe)



            # menu parameters
            # find middle section
            topOfMenu = int(height/4)
            bottomOfMenu = int((3*height)/4)
            numberOfSections = 3
            widthOfEachSection = (bottomOfMenu-topOfMenu)/numberOfSections
            firstSec = int(topOfMenu + widthOfEachSection)
            secondSec = int(topOfMenu + 2*widthOfEachSection)

            if ids_c is not None:
                length_ids_c = len(ids_c)
                ids_formatted_c = []
                for i in range(length_ids_c):
                    ids_formatted_c.append(ids_c[i][0])

                totalPosition = []
                totalAnimatePos = []
                # central aruco markers
                allArucos = [5,6,7,8,9,10,11,25,26,27,28,29]
                for i in allArucos:
                    if [i] in ids_c:
                        pos = ids_formatted_c.index(i)
                        TL = bbox_c[pos][0][0]
                        TR = bbox_c[pos][0][1]
                        BR = bbox_c[pos][0][2]
                        BL = bbox_c[pos][0][3]
                        c = np.array([(TL[0],TL[1]),(TR[0],TR[1]),(BR[0],BR[1]),(BL[0],BL[1])])
                        # find centre of aruco marker
                        M = cv2.moments(c)
                        cX = int(M["m10"] / M["m00"])
                        cY= int(M["m01"] / M["m00"])
                        # send coordinates to unity
                        totalPosition.append(i)
                        totalPosition.append(cX)
                        totalPosition.append(-cY)
                        totalPosition.append(0)
                    else:
                        totalPosition.append(i)
                        totalPosition.append(-100)
                        totalPosition.append(0)
                        totalPosition.append(0)
                        # position = [i,cX,-cY,0]
                        # posString = ','.join(map(str,position))
                        # print(posString)
                        # sock.sendall(posString.encode("UTF-8")

                menuPosition = []
                # edit animate data menu
                if [17] in ids_c:
                    pos = ids_formatted_c.index(17)
                    TL = bbox_c[pos][0][0]
                    TR = bbox_c[pos][0][1]
                    BR = bbox_c[pos][0][2]
                    BL = bbox_c[pos][0][3]
                    c = np.array([(TL[0],TL[1]),(TR[0],TR[1]),(BR[0],BR[1]),(BL[0],BL[1])])
                    # find centre of aruco marker
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY= int(M["m01"] / M["m00"])
                    # if in first box send "17,edit". if in second box send"17,animate". if third send "17,data"
                    menuPosition.append(17)
                    # print(cX,cY,0)
                    if cX<=100 and 200<cY<250:
                        status = True
                        menuPosition.append(0)
                        menuPosition.append("edit")
                    elif cX<=100 and 250<cY<300:
                        status = False
                        # paused frame
                        if ids_p is not None:
                            length_ids_p = len(ids_p)
                        ids_formatted_p = []
                        for i in range(length_ids_p):
                            ids_formatted_p.append(ids_p[i][0])
                        jointPistonArucos = [5,6,7,10,11]
                        for i in jointPistonArucos:
                            if [i] in ids_p:
                                pos = ids_formatted_p.index(i)
                                TL = bbox_p[pos][0][0]
                                TR = bbox_p[pos][0][1]
                                BR = bbox_p[pos][0][2]
                                BL = bbox_p[pos][0][3]
                                c = np.array([(TL[0],TL[1]),(TR[0],TR[1]),(BR[0],BR[1]),(BL[0],BL[1])])
                                # find centre of aruco marker
                                M = cv2.moments(c)
                                cX = int(M["m10"] / M["m00"])
                                cY= int(M["m01"] / M["m00"])
                                # send coordinates to unity
                                totalAnimatePos.append(i)
                                totalAnimatePos.append(cX)
                                totalAnimatePos.append(-cY)
                                totalAnimatePos.append(0)
                            else:
                                totalAnimatePos.append(i)
                                totalAnimatePos.append(-100)
                                totalAnimatePos.append(0)
                                totalAnimatePos.append(0)
                        menuAndSliderArucos = [8,9,25,26,27,28,29]
                        for i in menuAndSliderArucos:
                            if [i] in ids_c:
                                pos = ids_formatted_c.index(i)
                                TL = bbox_c[pos][0][0]
                                TR = bbox_c[pos][0][1]
                                BR = bbox_c[pos][0][2]
                                BL = bbox_c[pos][0][3]
                                c = np.array([(TL[0],TL[1]),(TR[0],TR[1]),(BR[0],BR[1]),(BL[0],BL[1])])
                                # find centre of aruco marker
                                M = cv2.moments(c)
                                cX = int(M["m10"] / M["m00"])
                                cY= int(M["m01"] / M["m00"])
                                # send coordinates to unity
                                totalAnimatePos.append(i)
                                totalAnimatePos.append(cX)
                                totalAnimatePos.append(-cY)
                                totalAnimatePos.append(0)
                            else:
                                totalAnimatePos.append(i)
                                totalAnimatePos.append(-100)
                                totalAnimatePos.append(0)
                                totalAnimatePos.append(0)
                        menuPosition.append(1)
                        menuPosition.append("animate")
                    else:
                        menuPosition.append(10)
                        menuPosition.append("none")
                else:
                    menuPosition.append(17)
                    menuPosition.append(10)
                    menuPosition.append("none")

                # stop animation
                # stopAnimation = []
                # if [25] in ids_c:
                #     pos = ids_formatted_c.index(25)
                #     TL = bbox_c[pos][0][0]
                #     TR = bbox_c[pos][0][1]
                #     BR = bbox_c[pos][0][2]
                #     BL = bbox_c[pos][0][3]
                #     c = np.array([(TL[0],TL[1]),(TR[0],TR[1]),(BR[0],BR[1]),(BL[0],BL[1])])
                #     # find centre of aruco marker
                #     M = cv2.moments(c)
                #     cX = int(M["m10"] / M["m00"])
                #     cY= int(M["m01"] / M["m00"])
                #     stopAnimation.append(25)
                #     stopAnimation.append(cX)
                #     stopAnimation.append(-cY)
                #     stopAnimation.append(0)
                # else:
                #     stopAnimation.append(25)
                #     stopAnimation.append(-100)
                #     stopAnimation.append(0)
                #     stopAnimation.append(0)

                #  hi


                # only send position when on the edit menu
                menuandtotal = totalPosition+menuPosition
                menuandtotalanimate = totalAnimatePos+menuPosition
                # newtotalPosString = ','.join(map(str,menuandtotalanimate))
                # totalPosString = ''
                pos17 = menuPosition.index(17)
                if menuPosition[pos17+1]==0:
                    totalPosString = ','.join(map(str,menuandtotal))
                    print(totalPosString)
                    sock.sendall(totalPosString.encode("UTF-8"))

                elif menuPosition[pos17+1]==1:
                    totalPosString = ','.join(map(str,menuandtotalanimate))
                    print(totalPosString)
                    sock.sendall(totalPosString.encode("UTF-8"))
                    # and newtotalPosString!=totalPosString
                elif menuPosition[pos17+1]==2:
                    totalPosString = ','.join(map(str,menuandtotalanimate))
                    print(totalPosString)
                    sock.sendall(totalPosString.encode("UTF-8"))



if __name__ == "__main__":
    main()