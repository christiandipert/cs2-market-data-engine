#include <string>
#include <iostream>

#include "generated/pricing.pb.h" // todo: fix not working

class Pricing {
    public:
        Pricing(std::string market_hash_name, float item_price, std::string market_source) {
            // do variable checks before setting
            this->market_hash_name = market_hash_name;
            this->item_price = item_price;
            this->market_source = market_source;
        }

        float get_item_price() {
            return this->item_price;
        }

        std::string get_market_hash_name() {
            return this->market_hash_name;
        }

        std::string get_market_source() {
            return this->market_source;
        }
            
    private:
        std::string market_hash_name;
        float item_price;
        std::string market_source;
};