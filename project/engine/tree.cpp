// Team: Ant Colony
// Members: Juan Camilo Méndez, Salomé Roldán
// File: tree.cpp — BST: Nest resource inventory + visited cells

#include <iostream>

// BST node structure
struct BSTNode {
    int key;              // Unique key: x*1000 + y
    float pheromone_value;
    int x, y;
    BSTNode* left;
    BSTNode* right;
};

class BSTree {
    private:
        BSTNode* root;

        BSTNode* insert(BSTNode* node, int key, float pheromone, int x, int y) {
            if (node == nullptr) {
                BSTNode* newNode = new BSTNode();
                newNode->key             = key;
                newNode->pheromone_value = pheromone;
                newNode->x               = x;
                newNode->y               = y;
                newNode->left            = nullptr;
                newNode->right           = nullptr;
                return newNode;
            }
            if      (key < node->key) node->left  = insert(node->left,  key, pheromone, x, y);
            else if (key > node->key) node->right = insert(node->right, key, pheromone, x, y);
            // Duplicated key: already exists, do nothing
            return node;
        }

        bool search(BSTNode* node, int key) {
            if (node == nullptr)  return false;
            if (key == node->key) return true;
            if (key < node->key)  return search(node->left,  key);
            else                  return search(node->right, key);
        }

        // Get pheromone value stored for a cell
        float getPheromone(BSTNode* node, int key) {
            if (node == nullptr)  return 0.0f;
            if (key == node->key) return node->pheromone_value;
            if (key < node->key)  return getPheromone(node->left,  key);
            else                  return getPheromone(node->right, key);
        }

        void destroy(BSTNode* node) {
            if (node == nullptr) return;
            destroy(node->left);
            destroy(node->right);
            delete node;
        }

    public:
        BSTree()  { root = nullptr; }
        ~BSTree() { destroy(root);  }

        // Insert a visited cell into the nest resource inventory
        void insertNode(int x, int y, float pheromone = 0.0) {
            int key = (x * 1000) + y;
            root = insert(root, key, pheromone, x, y);
        }

        // Check if a cell has already been visited
        bool isVisited(int x, int y) {
            int key = (x * 1000) + y;
            return search(root, key);
        }

        // Get stored pheromone value for a cell (nest resource lookup)
        float getResource(int x, int y) {
            int key = (x * 1000) + y;
            return getPheromone(root, key);
        }
}; // End BSTree class
