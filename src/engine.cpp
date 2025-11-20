#include "engine.hpp"
#include <stdexcept> // error gaming

void Database::set(const std::string& key, const std::string& value) {
	store[key] = value;
}

std::string Database::get(const std::string& key) {
	auto it = store.find(key);
	if (it != store.end()) {
		return it->second;
	}
	throw std::runtime_error("Key not found");
}