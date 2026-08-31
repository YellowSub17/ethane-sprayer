#include "pico/stdlib.h"
#include "main.h"
#include <stdio.h>


void other_function() {
    printf("wowee");
}



int main() {
    stdio_init_all();
    printf("hello");
    other_function();
    hello_world();

    while (true) {
        // --- Option 1: Test LED ---
        blink_led();
    }
    return 0;
}


