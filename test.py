import os
import sys
import time
import yaml
# select the given cuda device
# os.environ["CUDA_VISIBLE_DEVICES"]="5,6,7"
import torch
from torch.utils.data.dataloader import DataLoader
from utils import new_data_loader
from utils import model_factory

cuda_avail = torch.cuda.is_available()
# start_time = time.time()

def test_net(params):
    # Determine whether to use GPU
    if params['use_gpu'] == 1:
        print("GPU:" + str(params['use_gpu']))

    if params['use_gpu'] == 1 and cuda_avail:
        print("use_gpu=True and Cuda Available. Setting Device=CUDA")
        device = torch.device("cuda:0")  # change the GPU index based on the availability
        use_gpu = True
    else:
        print("Setting Device=CPU")
        device = torch.device("cpu")
        use_gpu = False


    # Set seed
    if params['use_random_seed'] == 0:
        torch.manual_seed(params['seed'])

    # Create network & Init Layer weights
    if params['Modality'] == "Combined":
        NN_model, model_params = model_factory.get_model(params, use_gpu)
    # Focus on using two sensor inputs
    elif params['Modality'] == "Tactile" or params['Modality'] == "Visual":
        NN_model, model_params = model_factory_single.get_model(params, use_gpu)


    if use_gpu:
        NN_model.cuda()

    # Dataloader
    test_dataset = new_data_loader.Tactile_Vision_dataset(params['Fruit_type'], params['label_encoding'],params["Tactile_scale_ratio"], params["Visual_scale_ratio"], params["video_length"],
                                                      data_path=params['Test_data_dir'])
    test_data_loader = DataLoader(test_dataset, batch_size=params['batch_size'], shuffle=True,
                                  num_workers=params['num_workers'])

    model_path = r"D:\dl\weight\great\timeSformer_orig_two_00158.pt"
    NN_model = torch.load(model_path)
    NN_model.eval()  # set the model to evaluation mode if needed NN_model.cuda() # move the model to GPU if needed


    # Start testing
    start_time = time.time()
    # Start
    test_total_acc = 0.0
    test_total_loss = 0.0
    test_total = 0.0
    # test_acc = 0
    for i, data in enumerate(test_data_loader):
        NN_model.zero_grad()
        label = data[2]
        if params['Modality'] == "Combined":
            output = NN_model(data[0], data[1])
        # Focus on two sensor input case
        elif params['Modality'] == "Visual":
            output = NN_model(data[0])
        elif params['Modality'] == "Tactile":
            output = NN_model(data[1])
        if use_gpu:
            label = label.to('cuda')
        # cal testing acc
        _, predicted = torch.max(output.data, 1)
        test_total_acc += (predicted == label).sum().item()
        test_total += len(label)
    test_total_acc = test_total_acc / test_total
    print('Test Acc: %.2f %%' % (test_total_acc * 100))
    print("Elapsed time: %f s" % (time.time() - start_time))


if __name__ == "__main__":
    exp_name = 'config_timeSformer.yaml' # make sure config.yaml is under the same directory

    if len(sys.argv) > 1:
        exp_name = sys.argv[1]  #or we can explicitly specify the file name

    print("Running Experiment: ", exp_name)
    yaml_file = exp_name
    if os.path.exists(yaml_file):
        with open(yaml_file) as stream:
            config_loaded = yaml.safe_load(stream)
    else:
        print("The yaml file does not exist!")
        sys.exit()
    test_net(config_loaded) # test the model, with the specifications

