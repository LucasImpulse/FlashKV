#pragma once
#include <string>
#include <unordered_map>
#include <fstream>

class Database {
public:
    Database(const std::string& filename);

    ~Database();

    void set(const std::string& key, const std::string& value);
    std::string get(const std::string& key);

private:
    std::unordered_map<std::string, std::string> store;

    std::ofstream db_file;

    void load_from_file(const std::string& filename);
};