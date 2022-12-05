import numpy
from PIL import ImageGrab
import pytesseract
import pyautogui
import time
import cv2
from multiprocessing import Process, Pool


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def get_column(curr_x, curr_y, num_in_column):
    # curr_x = 505
    # curr_y = 330
    width = 69
    height = 60
    column = ""
    for _ in range(num_in_column):
        im = ImageGrab.grab(bbox=(curr_x, curr_y, curr_x + width, curr_y + height))
        curr_y += 78  # to next row

        im = cv2.cvtColor(numpy.array(im), cv2.COLOR_BGR2GRAY)

        retval, im = cv2.threshold(im, 200, 255, cv2.THRESH_BINARY_INV)
        im = cv2.resize(im, (0, 0), fx=3, fy=3)
        temp_img = im.copy()
        im = cv2.GaussianBlur(im, (11, 11), cv2.BORDER_DEFAULT)
        im = cv2.medianBlur(im, 9)

        text = pytesseract.image_to_string(im, lang='eng',
                                           config='--psm 10 ')
        text = text[:-1].lower()
        if text == '':
            img = cv2.bilateralFilter(temp_img, 25, 80, 80)
            text = pytesseract.image_to_string(img, lang='eng',
                                               config='--psm 10 ')
            text = text[:-1].lower()
        if text == '':
            im = cv2.bilateralFilter(im, 25, 80, 80)
            # im = cv2.bilateralFilter(im, 15, 80, 80)
            text = pytesseract.image_to_string(im, lang='eng',
                                               config='--psm 10 ')
            text = text[:-1].lower()
        if text == '':
            text = 'b'

        #cv2.imshow('asd', im)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        if text == 'qu':
            text = 'q'
        if '0' in text:
            text = 'o'
        elif '@' in text:
            text = 'o'
        elif ')' in text:
            text = 'o'
        if '|' in text:
            text = 'i'
        elif '1' in text:
            text = 'i'
        elif '{' in text:
            text = 'i'
        if '5' in text:
            text = 's'
        elif '§' in text:
            text = 's'
        if '4' in text:
            text = 'p'
        elif 'pp' in text:
            text = 'p'
        elif ':' in text:
            text = 'p'
        if text[0] in ['\'', '"', '‘', '`']:
            text = text[1:]
        if len(text) == 2:
            text = text[1]
        column += text          # put all letters in an array first then use .join
    return column


def get_board():
    curr_x = 503
    params = []
    for idx in range(7):
        if idx % 2 == 0:
            curr_y = 330
            num = 7
        else:
            curr_y = 293
            num = 8
        args = (curr_x, curr_y, num)
        params.append(args)
        curr_x += 78
    with Pool() as pool:
        board = pool.starmap(get_column, params)
    return board


def alt_tab():
    pyautogui.hotkey('alt', 'tab')


if __name__ == '__main__':
    time.sleep(0.2)
    alt_tab()
    start_time = time.time()
    print(get_board())
    print(f"Time: {time.time() - start_time}")
    #print(pyautogui.position())
    alt_tab()
    #temp()


    # col 1 (505, 330, 7)
    # col 2 (583, 293, 8)
    # col 3 (661, 330, 7)
    # col 4 (745, 293, 8)
    # col 5 (825, 330, 7)
    # col 6 (905, 293, 8)
    # col 7 (973, 330, 7)


