#include "engine.hpp"
#include <iostream>
#include <stdexcept> // error gaming

Database::Database(const std::string& filename) {
	load_from_file(filename);

	db_file.open(filename, std::ios::app | std::ios::binary);
	if (!db_file.is_open()) {
		throw std::runtime_error("Cannot open database.");
	}
}

Database::~Database() {
	if (db_file.is_open()) {
		db_file.close();
	}
}

void Database::set(const std::string& key, const std::string& value) {
	store[key] = value;

	db_file << key << "," << value << "\n";
	db_file.flush();
}

std::string Database::get(const std::string& key) {
	auto it = store.find(key);
	if (it != store.end()) {
		return it->second;
	}
	throw std::runtime_error("Key not found");
}

void Database::load_from_file(const std::string& filename) {
	std::ifstream infile(filename);
	std::string line;

	while (std::getline(infile, line)) {
		size_t comma_pos = line.find(',');
		if (comma_pos != std::string::npos) {
			std::string key = line.substr(0, comma_pos);
			std::string value = line.substr(comma_pos + 1);
			store[key] = value;
		}
	}
}