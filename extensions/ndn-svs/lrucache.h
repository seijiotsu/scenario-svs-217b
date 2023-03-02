/*
* File:   lrucache.hpp
* Author: Alexander Ponomarev
*
* Created on June 20, 2013, 5:09 PM
*/

#ifndef _LRUCACHE_HPP_INCLUDED_
#define	_LRUCACHE_HPP_INCLUDED_

#include <unordered_map>
#include <list>
#include <cstddef>
#include <stdexcept>

namespace cache {

template<typename key_t>
class lru_cache {
public:
 typedef typename std::list<key_t>::iterator list_iterator_t;

 lru_cache() =default;

 void
 update(const key_t& key) {
   auto it = _cache_items_map.find(key);
   _cache_items_list.push_front(key);
   if (it != _cache_items_map.end()) {
     _cache_items_list.erase(it->second);
     _cache_items_map.erase(it);
   }
   _cache_items_map[key] = _cache_items_list.begin();

 }

 /*
  * modified: cache access interface changed
 const value_t& get(const key_t& key) {
   auto it = _cache_items_map.find(key);
   if (it == _cache_items_map.end()) {
     throw std::range_error("There is no such key in cache");
   } else {
     _cache_items_list.splice(_cache_items_list.begin(), _cache_items_list, it->second);
     return it->second->second;
   }
 }
  */

 std::list<key_t> get(){
   return _cache_items_list;
 }

 bool exists(const key_t& key) const {
   return _cache_items_map.find(key) != _cache_items_map.end();
 }

 size_t size() const {
   return _cache_items_map.size();
 }

private:
 std::list<key_t> _cache_items_list;
 std::unordered_map<key_t, list_iterator_t> _cache_items_map;
};

} // namespace cache

#endif	/* _LRUCACHE_HPP_INCLUDED_ */

