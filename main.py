import numpy as np
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader
from dataset import ReChordDataset
from model import CNNReChord


samples_per_beat = 3072
beats_per_window = 9
encode_length = 25 -1
data = [('01', '01'), ('01', '02'), ('01', '03'), ('01', '04'), ('01', '05'), ('01', '06'), ('01', '07'),
        ('01', '08'), ('01', '09'), ('01', '10'), ('01', '11'), ('01', '12'), ('01', '13'), ('01', '14'),
        ('02', '01'), ('02', '02'), ('02', '03'), ('02', '04'), ('02', '06'), ('02', '07'), ('02', '08'),
        ('02', '09'), ('02', '10'), ('02', '11'), ('02', '12'), ('02', '14'),
        ('03', '01'), ('03', '02'), ('03', '03'), ('03', '04'), ('03', '05'), ('03', '06'), ('03', '07'),
        ('03', '08'), ('03', '09'), ('03', '10'), ('03', '11'), ('03', '12'), ('03', '13'),
        ('06', '01'), ('06', '02'), ('06', '03'), ('06', '04'), ('06', '05'), ('06', '06'), ('06', '07'),
        ('06', '08'), ('06', '09'), ('06', '10'), ('06', '11'), ('06', '12'), ('06', '13'), ('06', '14'),
        ('07', '01'), ('07', '02'), ('07', '03'), ('07', '04'), ('07', '05'), ('07', '06'), ('07', '07'),
        ('07', '08'), ('07', '09'), ('07', '10'), ('07', '11'), ('07', '12'), ('07', '13'), ('07', '14'),
        ('12', '01'), ('12', '02'), ('12', '03'), ('12', '04'), ('12', '05'), ('12', '06'), ('12', '07'),
        ('12', '08'), ('12', '09'), ('12', '10'), ('12', '11'), ('12', '12')]


def load_data(batch_size, album, song):
    chord_dic = {}
    chord_dic['major'] = 0
    chord_dic['minor'] = 0
    features = np.empty([0, samples_per_beat * beats_per_window, 2])
    labels = np.empty([0, encode_length])

    # count the number of major and minor chords in this song
    feature_file = './data/features/{}_{}_{}.npy'.format(album, song, '0')
    label_file = './data/labels/{}_{}_{}.npy'.format(album, song, '0')
    features = np.concatenate((features, np.load(feature_file)), axis=0)
    labels = np.concatenate((labels, np.load(label_file)), axis=0)
    dataset = ReChordDataset(features, labels)
    for i in range(dataset.__len__()):
        for j in range(24):
            if dataset.y[i][j] == 1.0:
                if j % 2 == 0:
                    chord_dic['major'] += 1
                else:
                    chord_dic['minor'] += 1
                break

    features = np.empty([0, samples_per_beat * beats_per_window, 2])
    labels = np.empty([0, encode_length])

    for pitch in ['-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6']:
        feature_file = './data/features/{}_{}_{}.npy'.format(album, song, pitch)
        label_file = './data/labels/{}_{}_{}.npy'.format(album, song, pitch)
        tmp_feature = np.load(feature_file)
        tmp_label = np.load(label_file)
        arg_feature = np.empty([0, samples_per_beat * beats_per_window, 2])
        arg_label = np.empty([0, encode_length])
        count = 0
        m = 0
        n = 0

        if chord_dic['major'] > chord_dic['minor']:
            for m in range(tmp_label.shape[0]):
                for x in range(encode_length):
                    if tmp_label[m][x] == 1.0:
                        if x % 2 == 0:
                            count += 1
                            if count <= chord_dic['minor']:
                                arg_feature = np.concatenate((arg_feature, tmp_feature[m].reshape(1, tmp_feature.shape[1], tmp_feature.shape[2])), axis=0)
                                arg_label = np.concatenate((arg_label, tmp_label[m].reshape(1, tmp_label.shape[1])), axis=0)
                                # tmp_feature[m] = [[0, 0]]*samples_per_beat * beats_per_window
                                # tmp_label[m][x] = 0
                        else:
                            arg_feature = np.concatenate(
                                (arg_feature, tmp_feature[m].reshape(1, tmp_feature.shape[1], tmp_feature.shape[2])),
                                axis=0)
                            arg_label = np.concatenate((arg_label, tmp_label[m].reshape(1, tmp_label.shape[1])), axis=0)
                        break
                m += 1
        elif chord_dic['major'] < chord_dic['minor']:
            count = 0
            for n in range(tmp_label.shape[0]):
                for y in range(encode_length):
                    if tmp_label[n][y] == 1.0:
                        if y % 2 == 1:
                            count += 1
                            if count <= chord_dic['major']:
                                arg_feature = np.concatenate((arg_feature,
                                                              tmp_feature[m].reshape(1, tmp_feature.shape[1],
                                                                                     tmp_feature.shape[2])), axis=0)
                                arg_label = np.concatenate(
                                    (arg_label, tmp_label[m].reshape(1, tmp_label.shape[1])),
                                    axis=0)
                                # tmp_feature[n] = [[0, 0]] * samples_per_beat * beats_per_window
                                # tmp_label[n][y] = 0
                        else:
                            arg_feature = np.concatenate(
                                (arg_feature, tmp_feature[m].reshape(1, tmp_feature.shape[1], tmp_feature.shape[2])),
                                axis=0)
                            arg_label = np.concatenate((arg_label, tmp_label[m].reshape(1, tmp_label.shape[1])), axis=0)
                        break
                n += 1

        features = np.concatenate((features, arg_feature), axis=0)
        labels = np.concatenate((labels, arg_label), axis=0)




    train_data, val_data, train_label, val_label = train_test_split(features, labels, test_size=0.2)

    train_dataset = ReChordDataset(train_data, train_label)
    val_dataset = ReChordDataset(val_data, val_label)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader


def load_model(lr, config=0, pre_trained=-1):
    if pre_trained >= 0:
        model_file = './result/config{}/preliminary_model{}.pt'.format(config, pre_trained)
        model = torch.load(model_file)
        loss_fnc = torch.nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    else:
        model = CNNReChord(samples_per_beat, beats_per_window, config=config, mode='simple')
        loss_fnc = torch.nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    return model, loss_fnc, optimizer


def evaluate(model, val_loader):
    model.eval()
    total_correct = 0

    for i, vbatch in enumerate(val_loader):
        feats, label = vbatch
        feats = np.swapaxes(feats, 1, 2)
        predictions = model(feats.float())
        correct = predictions.argmax(dim=1) == label.argmax(dim=1)
        total_correct += int(correct.sum())

    return float(total_correct) / len(val_loader.dataset)


def data_balance():
    chord_dic = {}
    chord_dic['major'] = 0
    chord_dic['minor'] = 0

    features = np.empty([0, samples_per_beat * beats_per_window, 2])
    labels = np.empty([0, encode_length - 1])
    # album = '01'
    # song = '01'
    for album, song in data:
        feature_file = './data/features/{}_{}_{}.npy'.format(album, song, '0')
        label_file = './data/labels/{}_{}_{}.npy'.format(album, song, '0')
        features = np.concatenate((features, np.load(feature_file)), axis=0)
        labels = np.concatenate((labels, np.load(label_file)), axis=0)

    dataset = ReChordDataset(features, labels)

    for i in range(dataset.__len__()):
        for j in range(24):
            if dataset.y[i][j] == 1.0:
                if j % 2 == 0:
                    chord_dic['major'] += 1
                else:
                    chord_dic['minor'] += 1
                break

    return chord_dic


def main(batch_size, lr, epochs, config=0, pre_trained=-1):
    model, loss_fnc, optimizer = load_model(lr, config=config, pre_trained=pre_trained)

    for epoch in range(pre_trained + 1, epochs):
        print('Training epoch {} ...'.format(epoch))

        train_accuracy = []
        val_accuracy = []

        for album, song in data:
            print('\tAlbum {}, song {} ...'.format(album, song))

            train_loader, val_loader = load_data(batch_size, album, song)

            for i, batch in enumerate(train_loader):
                # get the inputs
                feats, label = batch
                feats = np.swapaxes(feats, 1, 2)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                predictions = model(feats.float())
                batch_loss = loss_fnc(input=predictions, target=label.float())

                batch_loss.backward()
                optimizer.step()

            train_acc = evaluate(model, train_loader)
            val_acc = evaluate(model, val_loader)

            train_accuracy.append(train_acc)
            val_accuracy.append(val_acc)

            print('\tFinished album {} song {} | Training accuracy: {} | Validation accuracy: {}'.format(
                album, song, train_acc, val_acc
            ))

        average_train_acc = sum(train_accuracy)/len(train_accuracy)
        average_val_acc = sum(val_accuracy)/len(val_accuracy)
        print('Finished epoch {} | Average training accuracy: {} | Average validation accuracy: {}'.format(
            epoch, average_train_acc, average_val_acc
        ))

        model_file_name = './result/config{}/preliminary_model{}.pt'.format(config, epoch)
        torch.save(model, model_file_name)
        with open('./result/config{}/result.txt'.format(config), 'a+') as file:
            file.write('Preliminary model %d: Average training accuracy: %.4f | Average validation accuracy: %.4f\n' % (
                epoch, average_train_acc, average_val_acc
            ))
        print('Model saved as {}.'.format(model_file_name))


if __name__ == "__main__":
    main(64, 0.001, 50, config=0, pre_trained=49)
