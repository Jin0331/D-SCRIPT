"""
Evaluate a trained model
"""

import sys, os
import argparse
import numpy as np
import pandas as pd
import torch
import h5py

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    precision_recall_curve,
    average_precision_score,
    roc_curve,
    roc_auc_score,
)
from tqdm import tqdm


def add_args(parser):
    parser.add_argument("--model", help="Trained prediction model", required=True)
    parser.add_argument("--test", help="Test Data", required=True)
    parser.add_argument(
        "--embedding", help="h5 file with embedded sequences", required=True
    )
    parser.add_argument("-o", "--outfile", help="Output file to write results")
    parser.add_argument("-d", "--device", default=-1, help="Compute device to use")
    return parser


def plot_eval_predictions(labels, predictions, path="figure"):

    pos_phat = predictions[labels == 1]
    neg_phat = predictions[labels == 0]

    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle("Distribution of Predictions")
    ax1.hist(pos_phat)
    ax1.set_xlim(0, 1)
    ax1.set_title("Positive")
    ax1.set_xlabel("p-hat")
    ax2.hist(neg_phat)
    ax2.set_xlim(0, 1)
    ax2.set_title("Negative")
    ax2.set_xlabel("p-hat")
    plt.savefig(path + ".phat_dist.png")
    plt.close()

    precision, recall, pr_thresh = precision_recall_curve(labels, predictions)
    aupr = average_precision_score(labels, predictions)
    print("AUPR:", aupr)

    plt.step(recall, precision, color="b", alpha=0.2, where="post")
    plt.fill_between(recall, precision, step="post", alpha=0.2, color="b")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title("Precision-Recall (AUPR: {:.3})".format(aupr))
    plt.savefig(path + ".aupr.png")
    plt.close()

    fpr, tpr, roc_thresh = roc_curve(labels, predictions)
    auroc = roc_auc_score(labels, predictions)
    print("AUROC:", auroc)

    plt.step(fpr, tpr, color="b", alpha=0.2, where="post")
    plt.fill_between(fpr, tpr, step="post", alpha=0.2, color="b")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title("Receiver Operating Characteristic (AUROC: {:.3})".format(auroc))
    plt.savefig(path + ".auroc.png")
    plt.close()


def main(args):
    device = int(args.device)

    # Load Model
    torch.cuda.set_device(device)
    use_cuda = device >= 0
    if device >= 0:
        print(
            "# Using CUDA device {} - {}".format(
                device, torch.cuda.get_device_name(device)
            )
        )
    else:
        print("# Using CPU")

    model_path = args.model
    if use_cuda:
        model = torch.load(model_path).cuda()
    else:
        model = torch.load(model_path).cpu()
        model.use_cuda = False

    embeddingPath = args.embedding
    h5fi = h5py.File(embeddingPath, "r")

    # Load Pairs
    test_fi = args.test
    test_df = pd.read_csv(test_fi, sep="\t", header=None)

    if args.outfile is None:
        outPath = "results"
        outFile = open("results.txt", "w+")
    else:
        outPath = args.outfile
        outFile = open(outPath + ".txt", "w+")

    allProteins = set(test_df[0]).union(test_df[1])

    seqEmbDict = {}
    for i in tqdm(allProteins, desc="Loading embeddings"):
        seqEmbDict[i] = torch.from_numpy(h5fi[i][:]).float()

    with torch.no_grad():
        phats = []
        labels = []
        for _, (n0, n1, label) in tqdm(
            test_df.iterrows(), total=len(test_df), desc="Predicting pairs"
        ):
            try:
                p0 = seqEmbDict[n0]
                p1 = seqEmbDict[n1]
                if use_cuda:
                    p0 = p0.cuda()
                    p1 = p1.cuda()

                pred = model.predict(p0, p1).item()
                phats.append(pred)
                labels.append(label)
                print("{}\t{}\t1\t{:.5}".format(n0, n1, pred), file=outFile)
            except Exception as e:
                sys.stderr.write("{} x {} - {}".format(n0, n1, e))

    phats = np.array(phats)
    labels = np.array(labels)
    plot_eval_predictions(labels, phats, outPath)

    outFile.close()
    h5fi.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser)
    main(parser.parse_args())