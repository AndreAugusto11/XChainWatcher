library(ggplot2)
library(dplyr)
library(gridExtra)
library(patchwork)
library(tidyr)
library(cowplot)

ronin_evaluation_data <- read.csv('../cross-chain-rules-validator/evaluations/ronin-bridge/output.csv')
nomad_evaluation_data <- read.csv('../cross-chain-rules-validator/evaluations/nomad-bridge/output.csv')

x_limits <- c(0.01, 100)
custom_breaks <- c(0.01, 0.1, 1, 10, 100)

ronin_evaluation_data <- ronin_evaluation_data %>%
    mutate(type = paste(type, "ronin", sep = "_"))

nomad_evaluation_data <- nomad_evaluation_data %>%
    mutate(type = paste(type, "nomad", sep = "_"))

combined_evaluation_data <- bind_rows(ronin_evaluation_data, nomad_evaluation_data)


# Create the first histogram for balance_at_date_capped
p1 <- ggplot(combined_evaluation_data, aes(x = time, color = type)) +
  stat_ecdf(geom = "step", alpha = 1) +
  scale_x_log10(limits = x_limits, breaks = custom_breaks, labels = scales::label_number()) +
  scale_color_manual(
    values = c("native_nomad" = "#1f77b4", "native_ronin" = "#da00ff", "non-native_nomad" = "#ff7f0e", "non-native_ronin" = "#c07a00"),
    labels = c("Nomad (Native): N = 7,656", "Ronin (Native): N = 468,997", "Nomad (Non-Native): N = 51,702", "Ronin (Non-Native): N = 347,580")
  ) +
  labs(
    title = "",
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
    axis.text = element_text(size = 10, face="bold"),
    legend.position = c(0.78, 0.28),
    legend.background = element_rect(fill="lightblue",
                                     size=0.5, linetype="solid", color="lightblue"),
    legend.text = element_text(size = 10),
    legend.title = element_blank(),
    
    #legend.position = "bottom",
    #legend.key.spacing.x = unit(0.2, 'cm'),
    #legend.text = element_text(size = 12, margin = margin(r = 2))
  )

p1
