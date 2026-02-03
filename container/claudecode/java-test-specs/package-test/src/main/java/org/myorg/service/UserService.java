package org.myorg.service;

public class UserService {

    public String processUser(String name) {
        if (name == null || name.isEmpty()) {
            return "Invalid user";
        }

        if (name.length() > 10) {
            return "Name too long: " + name;
        }

        return "Processed: " + name.toUpperCase();
    }

    public int calculateScore(int base) {
        if (base < 0) {
            return 0;
        }

        return base * 10 + 5;
    }
}