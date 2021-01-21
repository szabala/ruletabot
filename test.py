import pickle

server_channel_dict = dict()

with open('text_channels.pickle', 'wb') as handle:
        pickle.dump(server_channel_dict, handle)
