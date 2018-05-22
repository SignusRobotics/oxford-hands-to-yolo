# Convert Oxford Hand Dataset for YOLO

Information about the dataset can be found at 
[http://www.robots.ox.ac.uk/~vgg/data/hands/](http://www.robots.ox.ac.uk/~vgg/data/hands/)

First ```git clone``` this repository, then run the following commands to download, extract and create the required annotations for YOLO.

```bash
wget http://www.robots.ox.ac.uk/~vgg/data/hands/downloads/hand_dataset.tar.gz \
&& tar -xvzf hand_dataset.tar.gz \
&& python converter.py
```

Each of the training categories generates a new folder called new_annotations containing one text file pr image.

The files are in the format YOLO expects with one line pr annotated object:
```
0 0.781616 0.792040 0.079581 0.105805
0 0.458258 0.482815 0.048888 0.077585
```

## Annotation files
```
test: hand_dataset/test_dataset/test_data/new_annotations
train: hand_dataset/training_dataset/training_data/new_annotations
validation: hand_dataset/validation_dataset/validation_data/new_annotations
```

## Index files used by YOLO
```
test.txt
train.txt
validation.txt
```
