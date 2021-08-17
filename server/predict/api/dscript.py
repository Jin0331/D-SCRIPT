import sys

sys.path.append("../")

import os
from io import StringIO

import h5py
import pandas as pd
import torch
from dotenv import load_dotenv
from tqdm import tqdm

import dscript

load_dotenv()

import email
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dscript.fasta import parse_input
from dscript.language_model import lm_embed


def predict(
    seqs,
    pairsIndex,
    pairs,
    id,
    device=-1,
    modelPath="dscript-models/human_v1.sav",
    threshhold=0.5,
):
    """
    Given specified candidate pairs and protein sequences,
    Creates a .tsv file of interaction predictions and returns the url
    within 'server/tmp/predictions'
    """

    # Set Outpath
    outPath = f"tmp/predictions/{id}"

    # Set Device
    print("# Setting Device...")
    use_cuda = (device >= 0) and torch.cuda.is_available()
    if use_cuda:
        torch.cuda.set_device(device)
        print(
            f"# Using CUDA device {device} - {torch.cuda.get_device_name(device)}"
        )
    else:
        print("# Using CPU")

    # Load Model
    print("# Loading Model...")
    try:
        if use_cuda:
            model = torch.load(modelPath).cuda()
        else:
            model = torch.load(modelPath).cpu()
            model.use_cuda = False
    except FileNotFoundError:
        print(f"# Model {modelPath} not found")
        return

    # Load Sequences
    print("# Loading Sequences...")
    try:
        names, sequences = parse_input(seqs)
        seqDict = {n: s for n, s in zip(names, sequences)}
    except:
        return
    print(seqDict)

    # Load Pairs
    print("# Loading Pairs...")
    if pairsIndex in ["1", "2"]:
        try:
            pairs_array = pd.read_csv(StringIO(pairs), sep=",", header=None)
            all_prots = set(pairs_array.iloc[:, 0]).union(
                set(pairs_array.iloc[:, 1])
            )
        except:
            return
    elif pairsIndex == "3":
        try:
            all_prots = list(seqDict.keys())
            data = []
            for i in range(len(all_prots) - 1):
                for j in range(i + 1, len(all_prots)):
                    data.append([all_prots[i], all_prots[j]])
            pairs_array = pd.DataFrame(data)
        except:
            return

    # Generate Embeddings
    print("# Generating Embeddings...")
    embeddings = {}
    for n in tqdm(all_prots):
        embeddings[n] = lm_embed(seqDict[n], use_cuda)
    print(embeddings)

    # Make Predictions
    print("# Making Predictions...")
    n = 0
    outPathAll = f"{outPath}.tsv"
    outPathPos = f"{outPath}.positive.tsv"
    cmap_file = h5py.File(f"{outPath}.cmaps.h5", "w")
    model.eval()
    with open(outPathAll, "w+") as f:
        with open(outPathPos, "w+") as pos_f:
            with torch.no_grad():
                for _, (n0, n1) in tqdm(
                    pairs_array.iloc[:, :2].iterrows(), total=len(pairs_array)
                ):
                    n0 = str(n0)
                    n1 = str(n1)
                    if n % 50 == 0:
                        f.flush()
                    n += 1
                    p0 = embeddings[n0]
                    p1 = embeddings[n1]
                    if use_cuda:
                        p0 = p0.cuda()
                        p1 = p1.cuda()
                    try:
                        cm, p = model.map_predict(p0, p1)
                        p = p.item()
                        f.write(f"{n0}\t{n1}\t{p}\n")
                        if p >= threshhold:
                            pos_f.write(f"{n0}\t{n1}\t{p}\n")
                            cmap_file.create_dataset(
                                f"{n0}x{n1}", data=cm.squeeze().cpu().numpy()
                            )
                    except RuntimeError as e:
                        print(f"{n0} x {n1} skipped - Out of Memory")
    cmap_file.close()

    return outPathAll


def email_results(
    receiver_email,
    filename,
    id,
    title=None,
    sender_email="dscript.results@gmail.com",
):
    """
    Given a user email, target path for prediction file, and job id
    Emails the user the results of their job
    """
    print("# Emailing Results ...")
    if not title:
        subject = f"D-SCRIPT Results for {id}"
    else:
        subject = f"D-SCRIPT Results for {title} ({id})"
    body = f"These are the results of your D-SCRIPT prediction on job {id}"
    password = os.getenv("EMAIL_PWD")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # filename

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {id}.tsv",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
