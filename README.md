# Ice tracking

## 1 Problem Statement

Detecting air-ice and ice-rock boundaries from the given radar echogram.

## 2 Approaches

We have 3 different approaches to solve the problem: Simplified Bayes Net, HMM and HMM with human feedback.

### 2.1 Simplified Bayes Net

The structure of the bayes net used for this approach is shown below.

![simplified](/DocumentationImages/simplified.JPG)

Here the observed variable is the column and states are the rows, but since there is no dependencies b/w states, state to state transition is not possible.
Therefore, for the air-ice boundary the emission probability given a column is 1 for the pixel carrying maximum normalized edge strength value in that column, for all the other pixels in the column the emission probability given a column is 1. Correspondingly the same logic is applied for the ice-rock boundary but with the constraint that the ice-rock boundary is always below air-ice boundary and the minimum distance between air-ice boundary and ice-rock boundary is 10 pixels.

The boundary for this approach is marked in Yellow color on the output image.

### 2.2 HMM

The structure of the bayes net used for this approach is shown below.

![HMM](/DocumentationImages/hmm.JPG)

The observed variables and states are same as above. The transition probabilities for a given state is shown below.

![Transition_probabilities](/DocumentationImages/transition_prob.JPG)

The assumption here is that given that a pixel exists on a boundary in a given column, the possible pixel in the next column is either in the same row as the previous or, a row above or below it, or two rows above or below it.

Since there is dependencies between states, the emission probability for the air-ice boundary is the scaled edge strength, here the scaling is done such that the all the emission probabilities in a given column sum to 1. Correspondingly the same logic is applied for the ice-rock boundary but with the constraint that the emission probabilities for the states from the top of the image till 9 pixels below the air-ice boundary is zero.

The boundary for this approach is marked in Blue color on the output image.

### 2.3 HMM with human feedback

In this approach for each of the boundaries a point which lies on these boundaries is passed as input. While the previous approach is followed there are minor differences applied to it. First for the transition probability, if the next possible state is in the column in which the passed input exists then the only transition possible is from a state in previous column to the state (row) given in the input. Similarly the emission probability is equal to 1 for the input pixel passed and for all the other pixels in the same column the value is 0.

The boundary for this approach is marked in red color on the output image.

## 3 Challenges

Since the probabilities are very low values we faced the underflow problem, to overcome it the viterbi table is scaled after calculating the values of the all states for a given observation. The scalling is done such that the values of all states for a given observeration sum to one.

## 4 Results

Below are the few images containing the results.

For image 31.png with the human input for air_ice (23,22) and ice-rock (5,65).

Air-Ice boundary:

![31_air_ice_output](/DocumentationImages/31_air_ice_output.png)

Ice-Rock boundary:

![31_ice_rock_output](/DocumentationImages/31_ice_rock_output.png)

For image 16.png with the human input for air_ice (21,22) and ice-rock (99,41).

Air-Ice boundary:

![16_air_ice_output](/DocumentationImages/16_air_ice_output.png)

Ice-Rock boundary:

![16_ice_rock_output](/DocumentationImages/16_ice_rock_output.png)

## 5 References

1) <https://en.wikipedia.org/wiki/Viterbi_algorithm>
