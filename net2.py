import numpy as np
import random
import math
import csv

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def reverseSigmoid(x):
    return math.log(1/x - 1)

class net:
    def __init__(self, layers):
        #Create activation matrix
        # This will be a 2-d one 
        self.activation_matrix = [] #Define inital array
        self.error_matrix = [] 
        self.z_matrix = [] #Activation before it is sigmoided
        for layer_index,layer in enumerate(layers):
            self.activation_matrix.append([]) #for each layer add an additional array
            self.error_matrix.append([])
            self.z_matrix.append([])
            for i in range(0, layer):
                self.activation_matrix[layer_index].append(0)
                self.error_matrix[layer_index].append(0)
                self.z_matrix[layer_index].append(0)
        #Create weight matrix
        # This will be a 3d matrix with each x,y containing a 1-d array of weights
        # These arrays contain the data for getting the activation from the PREVIOUS layer of neurons
        self.weight_matrix = [0] * (len(layers))
        self.bias_matrix = [0] * len(layers)
        for layer_index, layer_size in enumerate(layers):
            
            # create an array for each node
            self.weight_matrix[layer_index] = [0] * layer_size
            self.bias_matrix[layer_index] = [0] * layer_size #This one is only 2-d
            for node_index in range(0, layers[layer_index]):
                # For each node create the weight array of length equal to the next layer
                self.weight_matrix[layer_index][node_index] = [0] * (layers[layer_index - 1])
        
        # Initialize all weights to a random value
        for layer_index, layer in enumerate(self.weight_matrix):
            for node_index, node in enumerate(layer):
                for weight_index, weight in enumerate(node):
                    self.weight_matrix[layer_index][node_index][weight_index] = (random.random() * 1) - 0.5
                    self.bias_matrix[layer_index][node_index] = (random.random() * 1) - 0.5
        
    def createActivationMatrix(self):
        self.activation_matrix = [] #Define inital array
        for layer_index,layer in enumerate(self.bias_matrix):
            self.activation_matrix.append([]) #for each layer add an additional array
            for i in range(0, len(self.bias_matrix[layer_index])):
                self.activation_matrix[layer_index].append(0)

    def activate(self, inputs):
        # self.createActivationMatrix()#reset activations
        # Check for correct number of inputs
        if(len(inputs) != len(self.activation_matrix[0])):
            return -1

        self.activation_matrix[0] = inputs
        for layer_index, layer in enumerate(self.weight_matrix):
            if(layer_index == 0):
                continue # skip input layer
            for node_index, node in enumerate(layer):
                # Compute sum of weights
                self.activation_matrix[layer_index][node_index] = np.matmul(self.activation_matrix[layer_index - 1], self.weight_matrix[layer_index][node_index])
                # Add the bias
                self.activation_matrix[layer_index][node_index] += self.bias_matrix[layer_index][node_index]
                # Assign z matrix
                self.z_matrix[layer_index][node_index] = self.activation_matrix[layer_index][node_index]
                # Normalize
                self.activation_matrix[layer_index][node_index] = sigmoid(self.activation_matrix[layer_index][node_index])
                # print(value)
        return self.activation_matrix
        
    def print(self):
        print(self.weight_matrix)
        
    def error(self, inputs, expected_outputs):
        err = 0
        for case_number, case_input in enumerate(inputs):
            #Assign for future ease
            outputs = self.activate(case_input)[-1]

            #Calculate the error for the output layer
            deltaC = np.subtract(expected_outputs[case_number], outputs)
            err += np.matmul(deltaC, deltaC)
        return err / len(inputs)

    def train(self, inputs, expected_outputs):

        if(len(inputs) != len(expected_outputs)):
            return -1
        #create so that it will hold over multiple iterations
        weight_change = []
        bias_change = []
        #This will determine how often we update the network. Smaller number means smaller batches
        cases_between_updates = 50
        #Set learning rate. Lower is slower learning
        learning_rate = 1
        #Now loop through the test cases
        for case_number, case_input in enumerate(inputs):
            #Assign for future ease
            outputs = self.activate(case_input)[-1]
            #get the error function output
            case_output = np.power(np.abs(np.subtract(outputs, expected_outputs[case_number])), 2)
            case_output = case_output / 2

            #Calculate the error for the output layer
            deltaC = np.subtract(expected_outputs[case_number], outputs)
            dSigmoid = np.subtract(outputs, np.multiply(outputs, outputs))
            error = np.multiply(deltaC, dSigmoid)

            #Assign output layer error
            self.error_matrix[-1] = error

            #do rest of errors
            for layer_index in range(len(self.activation_matrix) - 2, 0, -1):
                error = self.error_matrix[layer_index + 1]
                activations = self.activation_matrix[layer_index]
                first_part = np.matmul(np.transpose(self.weight_matrix[layer_index + 1]), error)
                #Get derivative of sigmoid function for all activations
                dSigmoid = np.subtract(activations, np.multiply(activations, activations))
                self.error_matrix[layer_index] = np.multiply(first_part, dSigmoid)


            # If it is the first set then create the weight_change/bias matrix

            if((case_number + 1) % cases_between_updates == 1):
                bias_change = self.error_matrix
                for layer_index in range(len(self.activation_matrix)):
                    weight_change.append([])
                for layer_index in range(len(self.activation_matrix) - 1, 0, -1):
                    for node in range(0, len(self.error_matrix[layer_index])):
                        weight_change[layer_index].append(np.multiply(self.activation_matrix[layer_index - 1], self.error_matrix[layer_index][node]))
                         
            else:
                # if not simply update it
                bias_change = np.add(bias_change, self.error_matrix) # Bias is essentially just a sum of the error_matrix
                for layer_index in range(len(self.activation_matrix) - 1, 0, -1):
                    for node in range(0, len(self.error_matrix[layer_index])):
                        weight_change[layer_index][node] = np.add(weight_change[layer_index][node], (np.multiply(self.activation_matrix[layer_index - 1], self.error_matrix[layer_index][node])))

            #apply transformations every 10 items
            if (case_number + 1) % cases_between_updates == 0:
                #divide changes by n
                for i in range(len(weight_change)):
                    weight_change[i] = np.divide(weight_change[i], (cases_between_updates / learning_rate))
                    bias_change[i] = np.divide(bias_change[i], cases_between_updates / learning_rate)
                #change values
                #First bias
                self.bias_matrix = bias_change
                #then weights
                for i in range(1, len(weight_change)):
                    self.weight_matrix[i] = np.add(self.weight_matrix[i], weight_change[i])
                #reset delta weight
                weight_change = []

    def test(self, inputs, predictedOut):
        correct = 0
        for case_number, case_input in enumerate(inputs):
            #Assign for future ease
            outputs = self.activate(case_input)[-1]
            currentBest = [-1, 0] #current best choice and score
            for i in range(len(outputs)):
                if(outputs[i] > currentBest[1]):
                    # if a higher score is found change choice to it
                    currentBest = [i, outputs[i]]
            #check ans
            for i in range(len(outputs)):
                if(predictedOut[case_number][i] == 1):
                    if(currentBest[0] == i):
                        correct += 1
        print("Got " + str(correct) + " correct")
        print("Got " + str(len(inputs) - correct) + " wrong")

