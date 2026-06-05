// ============================================================
// Team: Ant Colony | 
// Members: Juan Camilo Méndez, Salomé Roldán
// File: linked_list.cpp
// ============================================================

# include <iostream>
# include <fstream>

using namespace std;

//Coordinates Structure
struct Coord{
    int x;
    int y;
};
//Node Structure
struct ListNode{
    Coord coord;
    ListNode * next;
};

//Stack for the path the ant travels
class PathStack{
    private:
        ListNode * head;
    //Constructor: initializes the empty stack
    public: 
        PathStack (){
            head = nullptr; 
        }
    // Destructor: Frees memory when the program ends
    ~PathStack() {
        while (!isEmpty()) {
            pop();
            } 
        }
    //Verification for empty list
    bool isEmpty(){
        return head == nullptr;
    }
    //New position visited
    void push(int x, int y){
        ListNode * newNode = new ListNode;
        newNode ->coord.x = x;
        newNode ->coord.y = y;
        newNode -> next = head; //New node points old head
        head = newNode; //New node is now the head
    }
    //Delete and return last position visited
    Coord pop(){
        if (isEmpty()){
            std::cerr <<"Error. Trying to pop an empty list" << std::endl;
            return {-1,-1};
        }

        ListNode * temp = head; //Save the actual node
        Coord poppedCoord = temp -> coord; 
        head = head ->next; //New head is the new node

        delete temp; //deletes previous position
        return poppedCoord;
    }

    Coord SeeHead(){
        if (isEmpty()){
            return {-1,-1};
        }
        return head -> coord;
    }
}; //End PathStack class

//AVL tree's node 
