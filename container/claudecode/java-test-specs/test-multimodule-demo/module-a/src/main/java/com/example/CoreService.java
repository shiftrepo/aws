package com.example;

/**
 * Core business logic service
 */
public class CoreService {

    public String processData(String input) {
        if (input == null || input.isEmpty()) {
            return "EMPTY";
        }
        return input.toUpperCase();
    }

    public int calculateScore(int value) {
        if (value < 0) {
            return 0;
        } else if (value > 100) {
            return 100;
        } else {
            return value * 2;
        }
    }
}