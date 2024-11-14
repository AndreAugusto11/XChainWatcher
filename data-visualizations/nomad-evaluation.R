library(ggplot2)
library(dplyr)
library(gridExtra)
library(patchwork)
library(tidyr)
library(cowplot)

nomad_evaluation_data <- read.csv('../cross-chain-rules-validator/evaluations/nomad-bridge/output.csv')

x_limits <- c(0.01, 100)
custom_breaks <- c(0.01, 0.1, 1, 10, 100)

native_time_metrics <- nomad_evaluation_data %>%
  filter(type == "native") %>%
  summarise(
    size = n(),
    max_time = max(time, na.rm = TRUE),
    min_time = min(time, na.rm = TRUE),
    avg_time = mean(time, na.rm = TRUE),
    median_time = median(time, na.rm = TRUE),
    std_time = sd(time, na.rm = TRUE)
  )

non_native_time_metrics <- nomad_evaluation_data %>%
  filter(type == "non-native") %>%
  summarise(
    size = n(),
    max_time = max(time, na.rm = TRUE),
    min_time = min(time, na.rm = TRUE),
    avg_time = mean(time, na.rm = TRUE),
    median_time = median(time, na.rm = TRUE),
    std_time = sd(time, na.rm = TRUE)
  )

print(native_time_metrics)
print(non_native_time_metrics)

# Create the first histogram for balance_at_date_capped
p1 <- ggplot(nomad_evaluation_data, aes(x = time, color = type)) +
  stat_ecdf(geom = "step", alpha = 1) +
  scale_x_log10(limits = x_limits, breaks = custom_breaks, labels = scales::label_number()) +
  scale_color_manual(
    name = "Type of Token Transferred",
    values = c("native" = "#1f77b4", "non-native" = "#ff7f0e"),
    labels = c("  Native: N=7,656", "  Non-Native: N=51,702")
  ) +
  labs(
    x="Transaction Receipt Processing Time (seconds)",
    y="Cumulative Distribution"
  ) +
  theme_minimal() +
  theme(
    plot.margin = unit(c(0, 0.4, 0, 0), "cm"),
    plot.title = element_text(face = "bold", size = 15, hjust = 0.5, vjust=1),
    text = element_text(family = "serif"),
    axis.line = element_line(colour = "black"),
    panel.grid.major.y = element_line(color = 4, size = 0.1, linetype = 2),
    panel.grid.major.x = element_line(color = 4, size = 0.1, linetype = 2),
    panel.grid.minor.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    axis.title.y=element_text(size=12, face="bold"),
    axis.title.x=element_text(size=12, face="bold"),
    legend.title = element_text(face = "bold", size=14, margin = margin(r = 5)),
    axis.text = element_text(size = 10, face="bold"),
    legend.position = c(0.79, 0.22),
    legend.background = element_rect(fill="lightblue",
                                     size=0.5, linetype="solid", color="lightblue"),
    legend.text = element_text(size = 10),
    
    #legend.position = "bottom",
    #legend.key.spacing.x = unit(0.2, 'cm'),
    #legend.text = element_text(size = 12, margin = margin(r = 2))
  )

p1
