#include <iostream>

//AVL node structure
struct AVLNode{
    int key;
    float pheromone_value;
    int x, y;
    int height;
    AVLNode * left;
    AVLNode * right;
};

class AVLTree{
    private:
        AVLNode * root;

        int max(int a, int b) {
            return (a > b) ? a : b;
        }

        int height(AVLNode * node){
            if (node == nullptr) return 0;
            return node->height;
        }

        int Balance(AVLNode * node){
            if (node == nullptr) return 0;
            return height(node->left) - height(node->right);
        }

        AVLNode * rightRotation(AVLNode * y){
            AVLNode * x  = y->left;
            AVLNode * T2 = x->right;
            x->right = y;
            y->left  = T2;
            y->height = max(height(y->left), height(y->right)) + 1;
            x->height = max(height(x->left), height(x->right)) + 1;
            return x;
        }

        AVLNode * leftRotation(AVLNode * x){
            AVLNode * y  = x->right;
            AVLNode * T2 = y->left;
            y->left  = x;
            x->right = T2;
            x->height = max(height(x->left), height(x->right)) + 1;
            y->height = max(height(y->left), height(y->right)) + 1;
            return y;
        }

        AVLNode * insert(AVLNode * node, int key, float pheromone, int x, int y){
            if (node == nullptr){
                AVLNode * newNode = new AVLNode();
                newNode->key            = key;
                newNode->pheromone_value = pheromone;
                newNode->x              = x;
                newNode->y              = y;
                newNode->height         = 1;
                newNode->left           = nullptr;
                newNode->right          = nullptr;
                return newNode;
            }
            if      (key < node->key) node->left  = insert(node->left,  key, pheromone, x, y);
            else if (key > node->key) node->right = insert(node->right, key, pheromone, x, y);
            else return node; // Duplicated key = already visited

            node->height = 1 + max(height(node->left), height(node->right));
            int balance  = Balance(node);

            // Left-Left
            if (balance > 1  && key < node->left->key)
                return rightRotation(node);
            // Right-Right
            if (balance < -1 && key > node->right->key)
                return leftRotation(node);
            // Left-Right
            if (balance > 1  && key > node->left->key){
                node->left = leftRotation(node->left);
                return rightRotation(node);
            }
            // Right-Left
            if (balance < -1 && key < node->right->key){
                node->right = rightRotation(node->right);
                return leftRotation(node);
            }
            return node;
        }

        // BST search — returns true if key exists
        bool search(AVLNode * node, int key){
            if (node == nullptr)  return false;
            if (key == node->key) return true;
            if (key <  node->key) return search(node->left,  key);
            else                  return search(node->right, key);
        }

    public:
        AVLTree() { root = nullptr; }

        void insertNode(int x, int y, float pheromone = 0.0){
            int key = (x * 1000) + y;
            root = insert(root, key, pheromone, x, y);
        }

        bool isVisited(int x, int y){
            int key = (x * 1000) + y;
            return search(root, key);
        }
}; // End AVLTree class
