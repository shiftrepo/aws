package com.example;

import java.util.*;

/**
 * 基本的なデータ構造の実装サンプル
 * カバレッジテスト用のデモンストレーション
 */
public class DataStructures {

    /**
     * スタック実装（配列ベース）
     */
    public static class SimpleStack<T> {
        private List<T> items;
        private int maxSize;

        public SimpleStack(int maxSize) {
            this.items = new ArrayList<>();
            this.maxSize = maxSize;
        }

        public void push(T item) {
            if (items.size() >= maxSize) {
                throw new IllegalStateException("スタックが満杯です");
            }
            items.add(item);
        }

        public T pop() {
            if (isEmpty()) {
                throw new EmptyStackException();
            }
            return items.remove(items.size() - 1);
        }

        public T peek() {
            if (isEmpty()) {
                throw new EmptyStackException();
            }
            return items.get(items.size() - 1);
        }

        public boolean isEmpty() {
            return items.isEmpty();
        }

        public int size() {
            return items.size();
        }

        public void clear() {
            items.clear();
        }
    }

    /**
     * キュー実装（リンクリストベース）
     */
    public static class SimpleQueue<T> {
        private LinkedList<T> items;
        private int maxSize;

        public SimpleQueue(int maxSize) {
            this.items = new LinkedList<>();
            this.maxSize = maxSize;
        }

        public void enqueue(T item) {
            if (items.size() >= maxSize) {
                throw new IllegalStateException("キューが満杯です");
            }
            items.addLast(item);
        }

        public T dequeue() {
            if (isEmpty()) {
                throw new NoSuchElementException("キューが空です");
            }
            return items.removeFirst();
        }

        public T peek() {
            if (isEmpty()) {
                throw new NoSuchElementException("キューが空です");
            }
            return items.getFirst();
        }

        public boolean isEmpty() {
            return items.isEmpty();
        }

        public int size() {
            return items.size();
        }

        public void clear() {
            items.clear();
        }
    }

    /**
     * 単方向リンクリスト
     */
    public static class SimpleLinkedList<T> {
        private class Node {
            T data;
            Node next;

            Node(T data) {
                this.data = data;
                this.next = null;
            }
        }

        private Node head;
        private int size;

        public SimpleLinkedList() {
            this.head = null;
            this.size = 0;
        }

        public void add(T data) {
            Node newNode = new Node(data);
            if (head == null) {
                head = newNode;
            } else {
                Node current = head;
                while (current.next != null) {
                    current = current.next;
                }
                current.next = newNode;
            }
            size++;
        }

        public void addFirst(T data) {
            Node newNode = new Node(data);
            newNode.next = head;
            head = newNode;
            size++;
        }

        public T removeFirst() {
            if (head == null) {
                throw new NoSuchElementException("リストが空です");
            }
            T data = head.data;
            head = head.next;
            size--;
            return data;
        }

        public boolean remove(T data) {
            if (head == null) {
                return false;
            }

            if (head.data.equals(data)) {
                head = head.next;
                size--;
                return true;
            }

            Node current = head;
            while (current.next != null) {
                if (current.next.data.equals(data)) {
                    current.next = current.next.next;
                    size--;
                    return true;
                }
                current = current.next;
            }
            return false;
        }

        public boolean contains(T data) {
            Node current = head;
            while (current != null) {
                if (current.data.equals(data)) {
                    return true;
                }
                current = current.next;
            }
            return false;
        }

        public int size() {
            return size;
        }

        public boolean isEmpty() {
            return head == null;
        }

        public void clear() {
            head = null;
            size = 0;
        }

        public List<T> toList() {
            List<T> result = new ArrayList<>();
            Node current = head;
            while (current != null) {
                result.add(current.data);
                current = current.next;
            }
            return result;
        }
    }

    /**
     * 二分探索木
     */
    public static class BinarySearchTree {
        private class Node {
            int value;
            Node left;
            Node right;

            Node(int value) {
                this.value = value;
                this.left = null;
                this.right = null;
            }
        }

        private Node root;

        public void insert(int value) {
            root = insertRec(root, value);
        }

        private Node insertRec(Node node, int value) {
            if (node == null) {
                return new Node(value);
            }

            if (value < node.value) {
                node.left = insertRec(node.left, value);
            } else if (value > node.value) {
                node.right = insertRec(node.right, value);
            }

            return node;
        }

        public boolean search(int value) {
            return searchRec(root, value);
        }

        private boolean searchRec(Node node, int value) {
            if (node == null) {
                return false;
            }

            if (value == node.value) {
                return true;
            } else if (value < node.value) {
                return searchRec(node.left, value);
            } else {
                return searchRec(node.right, value);
            }
        }

        public int findMin() {
            if (root == null) {
                throw new NoSuchElementException("木が空です");
            }
            Node current = root;
            while (current.left != null) {
                current = current.left;
            }
            return current.value;
        }

        public int findMax() {
            if (root == null) {
                throw new NoSuchElementException("木が空です");
            }
            Node current = root;
            while (current.right != null) {
                current = current.right;
            }
            return current.value;
        }

        public int height() {
            return heightRec(root);
        }

        private int heightRec(Node node) {
            if (node == null) {
                return -1;
            }
            return 1 + Math.max(heightRec(node.left), heightRec(node.right));
        }

        public List<Integer> inorderTraversal() {
            List<Integer> result = new ArrayList<>();
            inorderRec(root, result);
            return result;
        }

        private void inorderRec(Node node, List<Integer> result) {
            if (node != null) {
                inorderRec(node.left, result);
                result.add(node.value);
                inorderRec(node.right, result);
            }
        }

        public boolean isEmpty() {
            return root == null;
        }

        public void clear() {
            root = null;
        }
    }

    /**
     * 優先度付きキュー（最小ヒープ）
     */
    public static class MinHeap {
        private List<Integer> heap;

        public MinHeap() {
            this.heap = new ArrayList<>();
        }

        public void insert(int value) {
            heap.add(value);
            bubbleUp(heap.size() - 1);
        }

        private void bubbleUp(int index) {
            while (index > 0) {
                int parentIndex = (index - 1) / 2;
                if (heap.get(index) >= heap.get(parentIndex)) {
                    break;
                }
                swap(index, parentIndex);
                index = parentIndex;
            }
        }

        public int extractMin() {
            if (heap.isEmpty()) {
                throw new NoSuchElementException("ヒープが空です");
            }

            int min = heap.get(0);
            int lastValue = heap.remove(heap.size() - 1);

            if (!heap.isEmpty()) {
                heap.set(0, lastValue);
                bubbleDown(0);
            }

            return min;
        }

        private void bubbleDown(int index) {
            while (true) {
                int leftChild = 2 * index + 1;
                int rightChild = 2 * index + 2;
                int smallest = index;

                if (leftChild < heap.size() && heap.get(leftChild) < heap.get(smallest)) {
                    smallest = leftChild;
                }
                if (rightChild < heap.size() && heap.get(rightChild) < heap.get(smallest)) {
                    smallest = rightChild;
                }

                if (smallest == index) {
                    break;
                }

                swap(index, smallest);
                index = smallest;
            }
        }

        public int peek() {
            if (heap.isEmpty()) {
                throw new NoSuchElementException("ヒープが空です");
            }
            return heap.get(0);
        }

        public boolean isEmpty() {
            return heap.isEmpty();
        }

        public int size() {
            return heap.size();
        }

        private void swap(int i, int j) {
            int temp = heap.get(i);
            heap.set(i, heap.get(j));
            heap.set(j, temp);
        }

        public void clear() {
            heap.clear();
        }
    }
}