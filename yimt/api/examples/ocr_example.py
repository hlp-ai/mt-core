from ocr.detect import OCRImpl

app = OCRImpl(ctpn_weight_path=r"D:\kidden\mt\open\github\mt-io\ocr\weights\weights-ctpnlstm-init.hdf5",
                  densenet_weight_path=r"D:\kidden\mt\ocr\latin\latin_dense.hdf5",
                  dict_path=r"D:\kidden\mt\open\github\mt-io\ocr\dictionary\latin_chars.txt")

image_path = "./en1.png"
texts = app.detect(image_path)
print('\n'.join(texts))
