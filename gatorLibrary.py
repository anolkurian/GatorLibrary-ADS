import time
import sys
from os.path import splitext
class BookNode:
    def __init__(self, bookId, bookName, authorName, availability):
        self.bookId = bookId 
        self.bookName = bookName
        self.authorName = authorName 
        self.availability = availability
        # Track who currently has the book checked out
        self.borrowedBy = None  
        # Use a heap to store reservation requests 
        self.reservations = BinaryMinHeap()  
   
    def addReservation(self, patronId, priorityNumber):
        # Get current timestamp for the reservation
        timestamp = time.time()  
        reservation = (priorityNumber, patronId, timestamp)
        self.reservations.insert(reservation)
        # Limit number of reservations 
        if len(self.reservations.heap) > 20:
            return "Wailist full"

    def getReservations(self):
        # Extract reservations from heap
        reservations = [] 
        while True:
            minentry = self.reservations.removeMin()
            if minentry is not None:
                # Get just the patron ID 
                patronId = minentry[1]  
                reservations.append(patronId)
            else:
                break
        return reservations

class RedBlackNode:
    def __init__(self, value: BookNode):
        self.value = value
        self.red = False
        self.parent = None
        self.l = None
        self.r = None
        
class RedBlackTree:
    def __init__(self):
        # Initialize sentinel leaf node
        self.nil = RedBlackNode(BookNode(0, None, None, None))  
        self.nil.red = False  
        self.nil.l = None
        self.nil.r = None
        self.root = self.nil
  
        # Track recoloring for balancing
        self.colorFlipCount = 0

    def insert(self, value):
        newNode = RedBlackNode(value) 
        newNode.red = True  
        # Initialize new node child pointers  
        newNode.l = self.nil
        newNode.r = self.nil
        
        parent = None
        current = self.root

        # Find spot to insert new node  
        while current != self.nil:
            parent = current  
            if newNode.value.bookId < current.value.bookId:
                current = current.l
            elif newNode.value.bookId > current.value.bookId:   
                current = current.r
            else:
                # Node already exists  
                return
        
        # Insert node in tree
        newNode.parent = parent
        if parent is None:
           self.root = newNode
        elif newNode.value.bookId < parent.value.bookId:
           parent.l = newNode
        else:
          parent.r = newNode

        # Balance tree after insert   
        self.fixInsert(newNode)

    def find(self, value):
        # Find Book in Tree
        value = int(value)  
        curr = self.root
        while curr != self.nil and value != curr.value.bookId:
            if value < curr.value.bookId:
                curr = curr.l
            elif value > curr.value.bookId: 
                curr = curr.r
        
        # Return node if found, else None  
        if curr == self.nil:
            return None
        else:
            return curr
    def rotateLeft(self, x):
        # Rotate Left
        y = x.r
        x.r = y.l
        if y.l != self.nil:
            y.l.parent = x
        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.l:
            x.parent.l = y
        else:
            x.parent.r = y
        y.l = x
        x.parent = y
    def rotateRight(self, x):
        # Rotate Right
        y = x.l
        x.l = y.r
        if y.r != self.nil:
            y.r.parent = x
        y.parent = x.parent
        if x.parent == None:
            self.root = y
        elif x == x.parent.r:
            x.parent.r = y
        else:
            x.parent.l = y
        y.r = x
        x.parent = y
    def delete(self, value):
        # Create an empty dictionary to store the color of each node before deletion
        dictBefore = {}
        # Create an empty stack and add the root node to it
        tempStack = []
        node = self.root
        tempStack.append(node)
        # Traverse the tree using BFS and store the color of each node in dictBefore
        while tempStack:
            curr = tempStack.pop(0)
            dictBefore[curr.value.bookId] = 1 if curr.red else 0
            if curr.l:
                tempStack.append(curr.l)
            if curr.r:
                tempStack.append(curr.r)
        # Find the node to be deleted
        z = self.find(value)
        if z is None:
            return
        y = z
        y_original_color = y.red
        # If z has no left child, replace z with its right child
        if z.l == self.nil:
            x = z.r
            self.transfer(z, z.r)
        # If z has no right child, replace z with its left child
        elif z.r == self.nil:
            x = z.l
            self.transfer(z, z.l)
        # If z has two children, replace z with its in-order successor
        else:
            y = self.minimum(z.r)
            y_original_color = y.red
            x = y.r
            if y.parent == z:
                x.parent = y
            else:
                self.transfer(y, y.r)
                y.r = z.r
                y.r.parent = y
            self.transfer(z, y)
            y.l = z.l
            y.l.parent = y
            y.red = z.red
        # Fix the tree if the original color of y was black
        if y_original_color == False:
            self.fixDelete(x, dictBefore)
        # Otherwise, update the color flip count
        else:
            dictAfter = {}
            tempStack = []
            node = self.root
            tempStack.append(node)
            while tempStack:
                curr = tempStack.pop(0)
                dictAfter[curr.value.bookId] = 1 if curr.red else 0
                if curr.l:
                    tempStack.append(curr.l)
                if curr.r:
                    tempStack.append(curr.r)
            diff = {x: dictBefore[x] == dictAfter[x] for x in dictBefore if x in dictAfter}
            incrementBy = 0
            for d in diff.values():
                if d == False:
                    incrementBy += 1
            self.colorFlipCount += incrementBy
    def fixInsert(self, newNode):
        while newNode != self.root and newNode.parent.red:
            if newNode.parent == newNode.parent.parent.r:
                u = newNode.parent.parent.l
                if u.red:
                    # Case 1: Recoloring
                    u.red = False
                    newNode.parent.red = False
                    newNode.parent.parent.red = True
                    if (
                        u == self.root
                        or newNode.parent == self.root
                        or newNode.parent.parent == self.root
                    ):
                        self.colorFlipCount += 2
                    else:
                        self.colorFlipCount += 3
                    newNode = newNode.parent.parent
                else:
                    # Case 2: Restructuring
                    if newNode == newNode.parent.l:
                        newNode = newNode.parent
                        self.rotateRight(newNode)
                    newNode.parent.red = False
                    newNode.parent.parent.red = True
                    if (
                        newNode.parent == self.root
                        or newNode.parent.parent == self.root
                    ):
                        if self.root.red == True:
                            self.colorFlipCount += 2
                        else:
                            self.colorFlipCount += 1
                    else:
                        self.colorFlipCount += 2
                    self.rotateLeft(newNode.parent.parent)
            else:
                # Similar as above
                u = newNode.parent.parent.r
                if u.red:
                    u.red = False
                    newNode.parent.red = False
                    newNode.parent.parent.red = True
                    if (
                        u == self.root
                        or newNode.parent == self.root
                        or newNode.parent.parent == self.root
                    ):
                        self.colorFlipCount += 2
                    else:
                        self.colorFlipCount += 3
                    newNode = newNode.parent.parent
                else:
                    if newNode == newNode.parent.r:
                        newNode = newNode.parent
                        self.rotateLeft(newNode)
                    newNode.parent.red = False
                    newNode.parent.parent.red = True
                    if (
                        newNode.parent == self.root
                        or newNode.parent.parent == self.root
                    ):
                        if self.root.red == True:
                            self.colorFlipCount += 2
                        else:
                            self.colorFlipCount += 1
                    else:
                        self.colorFlipCount += 2
                    self.rotateRight(newNode.parent.parent)
        self.root.red = False
    def fixDelete(self, x, dictBefore):
        # Restructuring and recoloring for delete operations, similar to fix insert.
        while x != self.root and x.red == False:
            if x == x.parent.l:
                w = x.parent.r
                if w.red:
                    w.red = False
                    x.parent.red = True
                    self.rotateLeft(x.parent)
                    w = x.parent.r
                if w.l.red == False and w.r.red == False:
                    w.red = True
                    x = x.parent
                else:
                    if w.r.red == False:
                        w.l.red = False
                        w.red = True
                        self.rotateRight(w)
                        w = x.parent.r
                    w.red = x.parent.red
                    x.parent.red = False
                    w.r.red = False
                    self.rotateLeft(x.parent)
                    x = self.root
            else:
                w = x.parent.l
                if w.red:
                    w.red = False
                    x.parent.red = True
                    self.rotateRight(x.parent)
                    w = x.parent.l
                if w.r.red == False and w.l.red == False:
                    w.red = True
                    x = x.parent
                else:
                    if w.l.red == False:
                        w.r.red = False
                        w.red = True
                        self.rotateLeft(w)
                        w = x.parent.l
                    w.red = x.parent.red
                    x.parent.red = False
                    w.l.red = False
                    self.rotateRight(x.parent)
                    x = self.root
        x.red = False
        dictAfter = {}
        tempStack = []
        node = self.root
        tempStack.append(node)
        while tempStack:
            curr = tempStack.pop(0)
            dictAfter[curr.value.bookId] = 1 if curr.red else 0
            if curr.l:
                tempStack.append(curr.l)
            if curr.r:
                tempStack.append(curr.r)
        diff = {x: dictBefore[x] == dictAfter[x] for x in dictBefore if x in dictAfter}
        incrementBy = 0
        for d in diff.values():
            if d == False:
                incrementBy += 1
        self.colorFlipCount += incrementBy
    def transfer(self, u, v):
        #Supporting code for transformation
        if u.parent is None:
            self.root = v
        elif u == u.parent.l:
            u.parent.l = v
        else:
            u.parent.r = v
        v.parent = u.parent
    def minimum(self, x):
        while x.l != self.nil:
            x = x.l
        return x

class BinaryMinHeap:
    def __init__(self):
        self.heap = []
    def __iter__(self):
        return iter(self.heap)
    def insert(self, element):
        self.heap.append(element)
        self.heapifyUp(len(self.heap) - 1)
    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        top = self.heap[0]
        self.heap[0] = self.heap.pop()
        self.heapifyDown()
        return top
    def heapifyUp(self, currentIndex):
        #Heapify Up: Reorganizes the heap after inserting an element
        while currentIndex > 0:
            parentIndex = (currentIndex - 1) // 2
            if self.heap[parentIndex][0] > self.heap[currentIndex][0] or (
                self.heap[parentIndex][0] == self.heap[currentIndex][0]
                and self.heap[parentIndex][2] > self.heap[currentIndex][2]
            ):
                self.swap(parentIndex, currentIndex)
                currentIndex = parentIndex
            else:
                break
    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    def removeMin(self):
        if not self.heap:
            return None
        minElement = self.heap[0]
        last_element = self.heap.pop()
        if self.heap:
            self.heap[0] = last_element
            self.heapifyDown()
        return minElement
    def heapifyDown(self):
        # Heapify Down: Adjusts the heap after removing the root element
        currentIndex = 0
        while True:
            leftChildInd = 2 * currentIndex + 1
            rightChildInd = 2 * currentIndex + 2
            smallest = currentIndex
            if leftChildInd < len(self.heap) and (
                self.heap[leftChildInd][0] < self.heap[smallest][0]
                or (
                    self.heap[leftChildInd][0] == self.heap[smallest][0]
                    and self.heap[leftChildInd][2] < self.heap[smallest][2]
                )
            ):
                smallest = leftChildInd
            if rightChildInd < len(self.heap) and (
                self.heap[rightChildInd][0] < self.heap[smallest][0]
                or (
                    self.heap[rightChildInd][0] == self.heap[smallest][0]
                    and self.heap[rightChildInd][2] < self.heap[smallest][2]
                )
            ):
                smallest = rightChildInd
            if smallest != currentIndex:
                self.swap(currentIndex, smallest)
                currentIndex = smallest
            else:
                break

class LibrarySystem:
    def __init__(self):
        self.bookTree = RedBlackTree()
        self.patrons = {}
    def colorFlipCount(self):
        return self.bookTree.colorFlipCount
    def quit(self):
        exit()
    def printBook(self, bookId):
        # Print 1 Book based on bookId
        node = self.bookTree.find(bookId)
        if node is not None:
            patron_ids = [patronId[1] for patronId in node.value.reservations.heap]
            details = (
                f"BookID = {node.value.bookId}\n"
                f"Title = {node.value.bookName}\n"
                f"Author = {node.value.authorName}\n"
                f"Availability = {node.value.availability}\n"
                f"BorrowedBy = {node.value.borrowedBy}\n"
                f"Reservations = {patron_ids}"
            )
            return details
        else:
            return f"Book {bookId} not found in the library."
    def printBooks(self, node, bookId1, bookId2):
        # Print books in range of given bookids
        detailsList = []
        def processBook(bookNode):
            patron_ids = [patronId[1] for patronId in bookNode.value.reservations.heap]
            details = (
                f"BookID = {bookNode.value.bookId}\n"
                f"Title = {bookNode.value.bookName}\n"
                f"Author = {bookNode.value.authorName}\n"
                f"Availability = {bookNode.value.availability}\n"
                f"BorrowedBy = {bookNode.value.borrowedBy}\n"
                f"Reservations = {patron_ids}"
            )
            detailsList.append(details)
        def inorderTraversal(node):
            nonlocal detailsList
            if node is not None:
                inorderTraversal(node.l)
                if (
                    isinstance(node.value, BookNode)
                    and bookId1 <= node.value.bookId <= bookId2
                ):
                    processBook(node)
                inorderTraversal(node.r)
        inorderTraversal(node)
        return detailsList
    def insertBook(
        self,
        bookId,
        bookName,
        authorName,
        availability,
        borrowedBy=None,
        reservationHeap=None,
    ):
    # Insert Book with given information
        newBook = BookNode(bookId, bookName, authorName, availability)
        newBook.availability = availability
        newBook.borrowedBy = borrowedBy
        if reservationHeap:
            newBook.reservations.heap = reservationHeap
        self.bookTree.insert(newBook)
    def borrowBook(self, patronId, bookId, patronPriority):
        # Borrow book and if not available add to reservation
        node = self.bookTree.find(bookId)
        if node is not None:
            if node.value.availability == '"Yes"':
                node.value.availability = '"No"'
                node.value.borrowedBy = patronId
                self.patrons
                return f"Book {bookId} Borrowed by Patron {patronId}"
            else:
                reservationAdded = node.value.addReservation(patronId, patronPriority)
                if reservationAdded == "Waitlist full":
                    return f"Waitlist for Book {bookId} is full. Cannot add reservation for Patron {patronId}"
                else:
                    return f"Book {bookId} Reserved by Patron {patronId}"
        else:
            return f"Book {bookId} is not available for borrowing."
    def returnBook(self, patronId, bookId):
        # Return Borrowed Book  based on bookId and allot to reserved patrons
        node = self.bookTree.find(bookId)
        opLine = ""
        if (
            node is not None
            and node.value.availability == '"No"'
            and node.value.borrowedBy == patronId
        ):
            if len(node.value.reservations.heap) > 0:
                reservedPatronId = node.value.reservations.heap.pop(0)
                node.value.borrowedBy = reservedPatronId[1]
                opLine = (
                    f"Book {bookId} Returned by Patron {patronId} \n \n"
                    f"Book {bookId} Allotted to Patron {node.value.borrowedBy}"
                )
            else:
                node.value.availability = '"Yes"'
                node.value.borrowedBy = None
                opLine = f"Book {bookId} Returned by Patron {patronId}"
        else:
            opLine = f"Book {bookId} cannot be returned by Patron {patronId}."
        return opLine
    def deleteBook(self, bookId):
        # Delete Book based on book Id
        node = self.bookTree.find(bookId)
        if node is not None:
            if node.value.reservations.heap:
                reservations = node.value.getReservations()
                self.cancelReservations(bookId, reservations)
                opLine = f"Book {bookId} is no longer available. Reservations made by Patrons {', '.join(str(reservation) for reservation in reservations)} have been cancelled!"
            else:
                opLine = f"Book {bookId} is no longer available."
            self.bookTree.delete(bookId)
        else:
            opLine = f"Book {bookId} not found."
        return opLine
    def cancelReservations(self, bookId, patrons):
        for patronId in patrons:
            patron = self.patrons.get(patronId, None)
            if patron is not None:
                patron.cancel_reservation(bookId)
    def findClosestBook(self, node, targetId):
        closestLower, closestHigher = self.findClosestBookHelper(node, targetId)
        detailsList = []
        if closestLower is not None and closestHigher is not None:
            distanceLower = abs(targetId - closestLower.value.bookId)
            distanceHigher = abs(targetId - closestHigher.value.bookId)
            if distanceLower < distanceHigher:
                details = self.getBookDetails(closestLower)
                detailsList.append(details)
            elif distanceHigher < distanceLower:
                details = self.getBookDetails(closestHigher)
                detailsList.append(details)
            else:
                if closestLower.value.bookId == closestHigher.value.bookId:
                    details = self.getBookDetails(closestLower)
                    detailsList.append(details)
                else:
                    details1 = self.getBookDetails(closestLower)
                    details2 = self.getBookDetails(closestHigher)
                    detailsList.append(details1)
                    detailsList.append(details2)
        elif closestLower is not None:
            details = self.getBookDetails(closestLower)
            detailsList.append(details)
        elif closestHigher is not None:
            details = self.getBookDetails(closestHigher)
            detailsList.append(details)
        return detailsList
    def getBookDetails(self, node):
        patron_ids = [patronId[1] for patronId in node.value.reservations.heap]
        return (
            f"BookID = {node.value.bookId}\n"
            f"Title = {node.value.bookName}\n"
            f"Author = {node.value.authorName}\n"
            f"Availability = {node.value.availability}\n"
            f"BorrowedBy = {node.value.borrowedBy}\n"
            f"Reservations = {patron_ids}"
        )
    def findClosestBookHelper(
        self, node, targetId, closestLower=None, closestHigher=None
    ):
        while node.value.bookId != 0:
            if node.value.bookId == targetId:
                return node, node
            elif node.value.bookId < targetId:
                closestLower = node
                node = node.r
            else:
                closestHigher = node
                node = node.l
        return closestLower, closestHigher

def main(inputFilename):
    # Main Driver Function
    library = LibrarySystem()
    with open(inputFilename, "r") as file:
        lines = file.readlines()
        outputLines = []
        def parseCommand(command_string):
            string_parts = command_string.split("(")
            command = string_parts[0].strip()
            if len(string_parts) > 1:
                arguments = string_parts[1].rstrip(")").split(",")
                arguments = [arg.strip() for arg in arguments]
                return command, arguments
            else:
                return command, []
        for line in lines:
            line = line.strip()
            outputLine = None
            if line == "Quit()":
                print("Quit")
                print("Output printed to file")
                outputLine = f"Program Terminated!!"
                outputLines.append(outputLine)
                break
            else:
                command, *args = parseCommand(line)
                print(command)
                args = args[0]
                if command == "InsertBook":
                    bookId, title, author, availability = (
                        args[0],
                        args[1],
                        args[2],
                        args[3],
                    )
                    library.insertBook(
                        int(bookId), title, author, availability, None, None
                    )
                elif command == "PrintBook":
                    bookId = args[0]
                    outputLine = library.printBook(bookId)
                elif command == "PrintBooks":
                    bookId1, bookId2 = args[0], args[1]
                    books = library.printBooks(
                        library.bookTree.root, int(bookId1), int(bookId2)
                    )
                    all_books = [f"{book}\n" for book in books]
                    outputLine = "\n".join(all_books)
                elif command == "FindClosestBook":
                    targetId = args[0]
                    closest_books = library.findClosestBook(
                        library.bookTree.root, int(targetId)
                    )
                    allClosestBooks = [f"{book}\n" for book in closest_books]
                    outputLine = "\n".join(allClosestBooks)
                elif command == "BorrowBook":
                    patronId, bookId, priority = args[0], args[1], args[2]
                    outputLine = library.borrowBook(
                        int(patronId), int(bookId), int(priority)
                    )
                elif command == "ReturnBook":
                    patronId, bookId = args
                    outputLine = library.returnBook(int(patronId), int(bookId))
                elif command == "DeleteBook":
                    bookId = args[0]
                    outputLine = library.deleteBook(int(bookId))
                elif command == "ColorFlipCount":
                    outputLine = f"Colour Flip Count: {library.bookTree.colorFlipCount}"
            if outputLine is not None:
                outputLines.append(outputLine)
                outputLines.append("\n")
    try:
        outputFilename = splitext(inputFilename)[0] + "_output_file.txt"
        with open(outputFilename, "w") as outputFile:
            for line in outputLines:
                outputFile.write(str(line) + "\n")
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 gator.py inputFilename")
        sys.exit(1)
    inputFilename = sys.argv[1]
    main(inputFilename)
