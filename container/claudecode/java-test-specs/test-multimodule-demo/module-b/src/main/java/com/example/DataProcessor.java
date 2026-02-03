package com.example;

import java.util.List;
import java.util.ArrayList;

/**
 * Data processing and validation service
 */
public class DataProcessor {

    public List<String> filterValid(List<String> items) {
        List<String> result = new ArrayList<>();
        for (String item : items) {
            if (item != null && !item.trim().isEmpty()) {
                result.add(item.trim());
            }
        }
        return result;
    }

    public boolean validateEmail(String email) {
        if (email == null || email.isEmpty()) {
            return false;
        }

        // Simple email validation
        if (!email.contains("@")) {
            return false;
        }

        String[] parts = email.split("@");
        if (parts.length != 2) {
            return false;
        }

        return !parts[0].isEmpty() && !parts[1].isEmpty() && parts[1].contains(".");
    }

    public double calculateAverage(List<Integer> numbers) {
        if (numbers == null || numbers.isEmpty()) {
            return 0.0;
        }

        double sum = 0;
        for (Integer num : numbers) {
            if (num != null) {
                sum += num;
            }
        }

        return sum / numbers.size();
    }
}