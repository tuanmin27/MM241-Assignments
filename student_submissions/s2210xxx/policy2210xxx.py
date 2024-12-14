from policy import Policy


class Level:
    def __init__(self, height, pos):
        self.height = height
        self.pos = pos


class Stock:
    def __init__(self, index: int, width: int, height: int, levels: tuple[Level, ...]):
        self.index = index
        self.width = width
        self.height = height
        self.levels: tuple[Level, ...] = levels
        self.is_new_level: bool = True
        self.is_full: bool = False

    def can_create_new_level(self, products, indices) -> bool:
        used_height = sum(level.height for level in self.levels)
        for idx in indices:
            prod = products[idx]
            prod_h = prod["size"][1]
            if prod_h + used_height <= self.height and prod["quantity"] > 0:
                return True
        return False

    def can_place(self, product_height: int) -> bool:
        if not self.levels:
            return True

        current_level = self.levels[-1]
        return current_level.pos + current_level.height + product_height <= self.height

    def create_new_level(self, height: int) -> None:
        if not self.levels:
            new_pos = 0
        else:
            new_pos = self.levels[-1].pos + self.levels[-1].height
        new_level = Level(height, new_pos)
        self.levels = (*self.levels, new_level)

    def get_current_level(self) -> Level:
        return self.levels[-1]


class StockManager:
    def __init__(self):
        self.stocks: list[Stock] = []

    def add_stock(self, stock: Stock) -> None:
        self.stocks.append(stock)

    @property
    def stock_indices(self) -> tuple[int, ...]:
        return tuple(stock.index for stock in self.stocks)

    def get_stock(self) -> Stock:
        return self.stocks[-1]


class Policy2210xxx(Policy):
    def __init__(self, policy_id: int = 1, log: bool = False):
        self.log = log
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"

        # Student code here
        if policy_id == 1:
            pass
        elif policy_id == 2:
            pass

        self.stock_manager = StockManager()

    def _get_sorted_stocks_indices(self, stocks) -> tuple[int, ...]:
        # Sort the stocks in the ascending order of the stock's height
        # Return the list of stock indices
        indices = sorted(range(len(stocks)),
                         key=lambda i: self._get_stock_size_(stocks[i])[1], reverse=True)
        return tuple(indices)

    def _get_sorted_products_indices(self, products) -> tuple[int, ...]:
        # Sort the products in the descending order of the product's height
        # Return the list of product indices
        indices = sorted(range(len(products)),
                         key=lambda i: products[i]["size"][1], reverse=True)
        return tuple(indices)

    def reset(self):
        self.stock_manager = StockManager()

    def get_action(self, observation, info):
        # Sorting the stocks
        stocks = observation["stocks"]
        sorted_stocks_indices = self._get_sorted_stocks_indices(stocks)

        # Sorting the products
        products = observation["products"]
        sorted_products_indices = self._get_sorted_products_indices(products)

        # Main Algorithm
        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = 0, 0

        i = 0
        while i < len(sorted_stocks_indices):
            idx = sorted_stocks_indices[i]
            stock = stocks[idx]
            stock_w, stock_h = self._get_stock_size_(stock)

            if idx not in self.stock_manager.stock_indices:
                my_stock: Stock = Stock(
                    index=idx, width=stock_w, height=stock_h, levels=())
                self.stock_manager.add_stock(my_stock)
            else:
                my_stock: Stock = self.stock_manager.get_stock()
                if idx != my_stock.index:
                    i += 1
                    continue

            # Choose a product that can be placed in the stock
            pos_x, pos_y = None, None
            j = 0
            while j < len(sorted_products_indices):
                prod_idx = sorted_products_indices[j]
                prod = products[prod_idx]
                prod_size = prod["size"]
                prod_w, prod_h = int(prod_size[0]), int(prod_size[1])

                if prod["quantity"] == 0:
                    j += 1
                    continue

                # Check if the product can be placed in the stock
                if prod_w <= stock_w and prod_h <= stock_h:
                    # Check if it is a new level
                    if my_stock.is_new_level:
                        # Check if the product can be placed in the new level
                        # If yes, initialize the new level
                        if my_stock.can_place(prod_h):
                            my_stock.create_new_level(prod_h)
                            my_stock.is_new_level = False
                        else:
                            j += 1
                            continue

                    current_level = my_stock.get_current_level()
                    # Check if the product can be placed in the current level
                    if prod_h <= current_level.height:
                        for x in range(stock_w - prod_w + 1):
                            if self._can_place_(stock, (x, current_level.pos), prod_size):
                                pos_x, pos_y = x, current_level.pos
                                break
                    # Move to the next product if the item cannot be placed in the current level
                    else:
                        j += 1
                        continue

                # If the product is placed, break the loop
                if pos_x is not None and pos_y is not None:
                    break

                j += 1

            # If a product is placed, break the loop to return the action
            if pos_x is not None and pos_y is not None:
                stock_idx = sorted_stocks_indices[i]
                break

            # If no product can be placed in the stock, continue to process
            # If the level does not reach the stock's height, move to the next level
            if my_stock.can_create_new_level(products, sorted_products_indices):
                my_stock.is_new_level = True
                continue

            # If the level reaches the stock's height, move to the next stock
            # Reset the level-related variables for the next stock
            i += 1

        if self.log:
            print("-" * 50)
            print(
                f"Stock index: {stock_idx} - Stock size: {stock_w}x{stock_h}")
            print(
                f"Incoming product: {prod_size} - Position: ({pos_x}, {pos_y})")
            # print(
            #     f"Current level: {self.level_pos} - Level height: {self.level_h}")
        if stock_idx == -1:
            print(observation["products"])
            raise Exception("No action is taken")

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}
