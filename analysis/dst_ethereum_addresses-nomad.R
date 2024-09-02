library(ggplot2)
library(dplyr)
library(gridExtra)
library(patchwork)
library(tidyr)

format_ether_value <- function(x) {
  sapply(x, function(val) {
    if (val < 1) {
      format(val, scientific = FALSE, nsmall = 5, decimal.mark = ".", big.mark = "")
    } else {
      format(round(val), big.mark = ",", scientific = FALSE)
    }
  })
}

data <- read.csv("cross-chain-rules-validator/analysis/nomad-bridge/data/dst_ethereum_addresses_with_ether.csv")

zero_balances <- data %>% filter(balance_at_date == 0)
print(nrow(zero_balances))

non_zero_balances <- data %>% filter(balance_at_date != 0)
print(nrow(non_zero_balances))

threshold <- 0.0011

x_limits <- c(0.0000001, 1000)
custom_breaks <- c(0.0000001, 0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 1, 10, 100, 1000)

data_before <- data %>% filter(timestamp < 1659389551)
p1 <- ggplot(data_before, aes(x=balance_at_date_ether)) +
  geom_histogram(bins=150, fill="steelblue", color="black", alpha=0.5) +
  geom_vline(xintercept = threshold, linetype="dashed", color="red") +
  scale_x_log10(limits = x_limits, breaks = custom_breaks, labels = function(x) {sapply(x, format_ether_value)}) +
  scale_y_continuous(limits = c(0, 30), labels = scales::comma) +
  annotate("text", x = 0.0002, y = 30, hjust = .5, label = paste(threshold, "ETH"), colour = "red", size=3.5, fontface="bold", family = "serif") +
  labs(title="a) distribution of balances of non-zero destination addresses in withdrawals before attack (n=446)",
       x="Balance (Ether)",
       y="Frequency"
  ) +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0, 0.4, 0.5, 0), "cm"),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black", linewidth = 0.5),
    panel.grid.major.y = element_line(color = 4, linewidth = 0.1, linetype = 2),
    panel.grid.major.x = element_line(color = 4, linewidth = 0.1, linetype = 2),
    plot.title = element_text(size = 10, hjust = 0.5, vjust=1),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y=element_text(size=12, face="bold"),
    axis.title.x=element_text(size=12, face="bold"),
    legend.title = element_text(face = "bold", size=14),
    axis.text = element_text(size = 10, face="bold"),
  ) 

data_after <- data %>% filter(timestamp >= 1659389551)
p2 <- ggplot(data_after, aes(x=balance_at_date_ether)) +
  geom_histogram(bins=150, fill="steelblue", color="black", alpha=0.5) +
  geom_vline(xintercept = threshold, linetype="dashed", color="red") +
  scale_x_log10(limits = x_limits, breaks = custom_breaks, labels = function(x) {sapply(x, format_ether_value)}) +
  scale_y_continuous(limits = c(0, 30), labels = scales::comma) +
  annotate("text", x = 0.0002, y = 30, hjust = .5, label = paste(threshold, "ETH"), colour = "red", size=3.5, fontface="bold", family = "serif") +
  labs(title="b) distribution of balances of non-zero destination addresses in withdrawals after attack (n=162)",
       x="Balance (Ether)",
       y="Frequency"
  ) +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0, 0.4, 0, 0), "cm"),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black", linewidth = 0.5),
    panel.grid.major.y = element_line(color = 4, linewidth = 0.1, linetype = 2),
    panel.grid.major.x = element_line(color = 4, linewidth = 0.1, linetype = 2),
    plot.title = element_text(size = 10, hjust = 0.5, vjust=1),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y=element_text(size=12, face="bold"),
    axis.title.x=element_text(size=12, face="bold"),
    legend.title = element_text(face = "bold", size=14),
    axis.text = element_text(size = 10, face="bold"),
  ) 

combined_plot <- grid.arrange(p1, p2, ncol=1)

# ggsave("analysis/figures/dst_ethereum_addresses_with_ether_v2.pdf", combined_plot, width = 10, height = 16)