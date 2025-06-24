import torch
from torchvision import models, transforms
import torch.nn as nn
from PIL import Image
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("SELECTED DEVICE: ", device)

transform = transforms.Compose(
    [
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ]
)


bio_feature_filteration_model = models.resnet50()
for param in bio_feature_filteration_model.parameters():
    param.requires_grad = False


bio_feature_filteration_model.fc = nn.Sequential(
    nn.Dropout(0.5), nn.Linear(bio_feature_filteration_model.fc.in_features, 2)
)
bio_feature_filteration_model = bio_feature_filteration_model.to(device)

bio_feature_filteration_model.load_state_dict(
    torch.load(r"models\bio_non_bio_filter_model.pth")
)

# FOR HPV CLASSIFICAITON, LOADING A DIFFERENT MODEL CONFIG WITH DIFFERENT WEIGHT.

hpv_classifier = models.resnet50()

for name, param in hpv_classifier.named_parameters():
    if "layer4" not in name:
        param.requires_grad = False

for param in hpv_classifier.parameters():
    param.requires_grad = False

hpv_classifier.fc = nn.Sequential(
    nn.Dropout(0.5), nn.Linear(hpv_classifier.fc.in_features, 2)
)
hpv_classifier = hpv_classifier.to(device)
hpv_classifier = nn.DataParallel(hpv_classifier)

hpv_classifier.load_state_dict(torch.load(r"models\hpv_classifier.pth"))


def hpv_model(image_path, model_type, threshold=0.75):

    img = Image.open(image_path).convert("RGB")
    img_tensor = transform(img).unsqueeze(0).to(device)

    if model_type == "biological_filter":
        bio_feature_filteration_model.eval()
        with torch.no_grad():
            output = bio_feature_filteration_model(img_tensor)
            probs = torch.softmax(output, dim=1)
            confidence, prediction = torch.max(probs, dim=1)
            if prediction != 0:
                os.remove(image_path)
            if confidence.item() < threshold:
                os.remove(image_path)
                return "other", confidence.item()
            else:
                return (
                    prediction.item(),
                    confidence.item(),
                )  # class 0 means biological features founded.

    elif model_type == "hpv_classifier":
        hpv_classifier.eval()
        with torch.no_grad():
            output = hpv_classifier(img_tensor)
            probs = torch.softmax(output, dim=1)
            confidence, prediction = torch.max(probs, dim=1)
            if confidence.item() < threshold:
                return "other", confidence.item()
            else:
                return (
                    prediction.item(),
                    confidence.item(),
                )  # class 0 means hpv features found in the given image.
