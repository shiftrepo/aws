package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

import java.util.EmptyStackException;
import java.util.List;
import java.util.NoSuchElementException;

/**
 * @TestModule DataStructuresModule
 * @TestCase DataStructureOperations
 * @BaselineVersion 1.0.0
 * @TestType Data structure implementation testing for C1 coverage
 * @TestObjective Verify correct implementation of various data structures
 * @PreCondition Data structures must handle edge cases and errors properly
 * @ExpectedResult All data structure operations should work correctly
 * @TestData DeveloperTeam
 * @CreatedDate 2026-01-07
 */
@DisplayName("DataStructures Test Suite with Full Coverage")
public class DataStructuresTest {

    /**
     * @TestCase testSimpleStack
     * @TestType Functional
     * @TestObjective スタック操作のテスト
     * @ExpectedResult 正しいスタック操作
     */
    @Test
    @DisplayName("SimpleStackのテスト")
    void testSimpleStack() {
        DataStructures.SimpleStack<Integer> stack = new DataStructures.SimpleStack<>(3);

        // 初期状態
        assertTrue(stack.isEmpty());
        assertEquals(0, stack.size());

        // Push操作
        stack.push(1);
        stack.push(2);
        stack.push(3);
        assertEquals(3, stack.size());
        assertFalse(stack.isEmpty());

        // スタック満杯
        assertThrows(IllegalStateException.class, () -> stack.push(4));

        // Peek操作
        assertEquals(3, stack.peek());
        assertEquals(3, stack.size()); // サイズは変わらない

        // Pop操作
        assertEquals(3, stack.pop());
        assertEquals(2, stack.pop());
        assertEquals(1, stack.size());

        // Clear操作
        stack.clear();
        assertTrue(stack.isEmpty());
        assertEquals(0, stack.size());

        // 空スタックでの例外
        assertThrows(EmptyStackException.class, () -> stack.pop());
        assertThrows(EmptyStackException.class, () -> stack.peek());
    }

    /**
     * @TestCase testSimpleQueue
     * @TestType Functional
     * @TestObjective キュー操作のテスト
     * @ExpectedResult 正しいキュー操作
     */
    @Test
    @DisplayName("SimpleQueueのテスト")
    void testSimpleQueue() {
        DataStructures.SimpleQueue<String> queue = new DataStructures.SimpleQueue<>(3);

        // 初期状態
        assertTrue(queue.isEmpty());
        assertEquals(0, queue.size());

        // Enqueue操作
        queue.enqueue("first");
        queue.enqueue("second");
        queue.enqueue("third");
        assertEquals(3, queue.size());
        assertFalse(queue.isEmpty());

        // キュー満杯
        assertThrows(IllegalStateException.class, () -> queue.enqueue("fourth"));

        // Peek操作
        assertEquals("first", queue.peek());
        assertEquals(3, queue.size()); // サイズは変わらない

        // Dequeue操作（FIFO）
        assertEquals("first", queue.dequeue());
        assertEquals("second", queue.dequeue());
        assertEquals(1, queue.size());

        // Clear操作
        queue.clear();
        assertTrue(queue.isEmpty());
        assertEquals(0, queue.size());

        // 空キューでの例外
        assertThrows(NoSuchElementException.class, () -> queue.dequeue());
        assertThrows(NoSuchElementException.class, () -> queue.peek());
    }

    /**
     * @TestCase testSimpleLinkedList
     * @TestType Functional
     * @TestObjective リンクリスト操作のテスト
     * @ExpectedResult 正しいリンクリスト操作
     */
    @Test
    @DisplayName("SimpleLinkedListのテスト")
    void testSimpleLinkedList() {
        DataStructures.SimpleLinkedList<Integer> list = new DataStructures.SimpleLinkedList<>();

        // 初期状態
        assertTrue(list.isEmpty());
        assertEquals(0, list.size());

        // Add操作
        list.add(1);
        list.add(2);
        list.add(3);
        assertEquals(3, list.size());
        assertFalse(list.isEmpty());

        // AddFirst操作
        list.addFirst(0);
        assertEquals(4, list.size());

        // Contains操作
        assertTrue(list.contains(2));
        assertFalse(list.contains(5));

        // RemoveFirst操作
        assertEquals(0, list.removeFirst());
        assertEquals(3, list.size());

        // Remove操作
        assertTrue(list.remove(2));
        assertEquals(2, list.size());
        assertFalse(list.remove(10)); // 存在しない要素

        // ToList操作
        List<Integer> values = list.toList();
        assertEquals(2, values.size());
        assertEquals(1, values.get(0));
        assertEquals(3, values.get(1));

        // Clear操作
        list.clear();
        assertTrue(list.isEmpty());
        assertEquals(0, list.size());

        // 空リストでの例外
        assertThrows(NoSuchElementException.class, () -> list.removeFirst());

        // Remove from empty list
        assertFalse(list.remove(1));

        // Remove head element
        list.add(5);
        assertTrue(list.remove(5));
        assertTrue(list.isEmpty());
    }

    /**
     * @TestCase testBinarySearchTree
     * @TestType Functional
     * @TestObjective 二分探索木操作のテスト
     * @ExpectedResult 正しい二分探索木操作
     */
    @Test
    @DisplayName("BinarySearchTreeのテスト")
    void testBinarySearchTree() {
        DataStructures.BinarySearchTree bst = new DataStructures.BinarySearchTree();

        // 初期状態
        assertTrue(bst.isEmpty());

        // Insert操作
        bst.insert(50);
        bst.insert(30);
        bst.insert(70);
        bst.insert(20);
        bst.insert(40);
        bst.insert(60);
        bst.insert(80);
        assertFalse(bst.isEmpty());

        // Search操作
        assertTrue(bst.search(30));
        assertTrue(bst.search(70));
        assertTrue(bst.search(20));
        assertFalse(bst.search(100));
        assertFalse(bst.search(25));

        // 同じ値の挿入（重複）
        bst.insert(50);
        assertTrue(bst.search(50));

        // Min/Max操作
        assertEquals(20, bst.findMin());
        assertEquals(80, bst.findMax());

        // Height操作
        assertEquals(2, bst.height());

        // InorderTraversal操作
        List<Integer> inorder = bst.inorderTraversal();
        assertEquals(7, inorder.size());
        assertEquals(20, inorder.get(0));
        assertEquals(30, inorder.get(1));
        assertEquals(40, inorder.get(2));
        assertEquals(50, inorder.get(3));
        assertEquals(60, inorder.get(4));
        assertEquals(70, inorder.get(5));
        assertEquals(80, inorder.get(6));

        // Clear操作
        bst.clear();
        assertTrue(bst.isEmpty());
        assertFalse(bst.search(50));

        // 空の木での例外
        assertThrows(NoSuchElementException.class, () -> bst.findMin());
        assertThrows(NoSuchElementException.class, () -> bst.findMax());

        // 空の木の高さ
        assertEquals(-1, bst.height());

        // 空の木のトラバーサル
        assertTrue(bst.inorderTraversal().isEmpty());

        // 単一ノードの木
        bst.insert(100);
        assertEquals(0, bst.height());
        assertEquals(100, bst.findMin());
        assertEquals(100, bst.findMax());
    }

    /**
     * @TestCase testMinHeap
     * @TestType Functional
     * @TestObjective 最小ヒープ操作のテスト
     * @ExpectedResult 正しい最小ヒープ操作
     */
    @Test
    @DisplayName("MinHeapのテスト")
    void testMinHeap() {
        DataStructures.MinHeap heap = new DataStructures.MinHeap();

        // 初期状態
        assertTrue(heap.isEmpty());
        assertEquals(0, heap.size());

        // Insert操作
        heap.insert(50);
        heap.insert(30);
        heap.insert(70);
        heap.insert(20);
        heap.insert(40);
        heap.insert(60);
        heap.insert(80);
        assertEquals(7, heap.size());
        assertFalse(heap.isEmpty());

        // Peek操作（最小値）
        assertEquals(20, heap.peek());
        assertEquals(7, heap.size()); // サイズは変わらない

        // ExtractMin操作
        assertEquals(20, heap.extractMin());
        assertEquals(30, heap.extractMin());
        assertEquals(40, heap.extractMin());
        assertEquals(4, heap.size());

        // ヒープ性質の維持確認
        assertEquals(50, heap.peek());

        // 残りの要素を抽出
        assertEquals(50, heap.extractMin());
        assertEquals(60, heap.extractMin());
        assertEquals(70, heap.extractMin());
        assertEquals(80, heap.extractMin());
        assertTrue(heap.isEmpty());

        // 空ヒープでの例外
        assertThrows(NoSuchElementException.class, () -> heap.extractMin());
        assertThrows(NoSuchElementException.class, () -> heap.peek());

        // 同じ値の挿入
        heap.insert(10);
        heap.insert(10);
        heap.insert(5);
        heap.insert(15);
        assertEquals(5, heap.extractMin());
        assertEquals(10, heap.extractMin());
        assertEquals(10, heap.extractMin());
        assertEquals(15, heap.extractMin());

        // Clear操作
        heap.insert(100);
        heap.insert(200);
        heap.clear();
        assertTrue(heap.isEmpty());
        assertEquals(0, heap.size());
    }

    /**
     * @TestCase testComplexStackOperations
     * @TestType Edge Cases
     * @TestObjective スタックの複雑な操作とエッジケース
     * @ExpectedResult すべての操作が正しく動作
     */
    @Test
    @DisplayName("スタックの複雑な操作テスト")
    void testComplexStackOperations() {
        DataStructures.SimpleStack<String> stack = new DataStructures.SimpleStack<>(5);

        // 複数の操作を組み合わせる
        stack.push("A");
        stack.push("B");
        assertEquals("B", stack.pop());
        stack.push("C");
        stack.push("D");
        assertEquals("D", stack.peek());
        stack.push("E");
        stack.push("F");
        assertEquals(5, stack.size()); // A, C, D, E, F = 5要素

        // サイズ境界でのテスト
        assertThrows(IllegalStateException.class, () -> stack.push("G"));
        assertEquals(5, stack.size()); // サイズは変わらない

        // クリア後の再利用
        stack.clear();
        stack.push("X");
        assertEquals("X", stack.peek());
        assertEquals(1, stack.size());
    }

    /**
     * @TestCase testQueueEdgeCases
     * @TestType Edge Cases
     * @TestObjective キューのエッジケーステスト
     * @ExpectedResult すべてのエッジケースが正しく処理される
     */
    @Test
    @DisplayName("キューのエッジケーステスト")
    void testQueueEdgeCases() {
        DataStructures.SimpleQueue<Integer> queue = new DataStructures.SimpleQueue<>(2);

        // サイズ1のキュー
        queue.enqueue(100);
        assertEquals(100, queue.peek());
        assertEquals(100, queue.dequeue());
        assertTrue(queue.isEmpty());

        // 満杯→空→満杯のサイクル
        queue.enqueue(1);
        queue.enqueue(2);
        assertThrows(IllegalStateException.class, () -> queue.enqueue(3));
        queue.dequeue();
        queue.enqueue(3); // 再度追加可能
        assertEquals(2, queue.size());
    }
}